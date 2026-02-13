# 📚 Ejemplos de Uso y Extensiones

## Tabla de Contenidos
- [Ejecución Básica](#ejecución-básica)
- [Modificar Parámetros](#modificar-parámetros)
- [Agregar Validadores Bizantinos](#agregar-validadores-bizantinos)
- [Simular Particiones de Red](#simular-particiones-de-red)
- [Análisis de Datos](#análisis-de-datos)
- [Visualización](#visualización)

---

## 🚀 Ejecución Básica

### Ejemplo 1: Simulación Estándar
```bash
python3 simulate.py
```

### Ejemplo 2: Guardar Output
```bash
python3 simulate.py > output.log 2>&1
tail -f output.log  # Ver en tiempo real
```

### Ejemplo 3: Ver Solo Slots Específicos
```bash
# Ver solo cada 5 slots
python3 simulate.py | grep "Slot [0-9]*5\]"

# Ver slots 50-60
python3 simulate.py | awk '/Slot 5[0-9]/ || /Slot 60/'
```

---

## ⚙️ Modificar Parámetros

### Ejemplo 4: Red Grande (100 validadores)

**Archivo:** `simulate_large.py`
```python
from consensus import State, Block, Config, compute_hash
from p2p import Staker, P2PNetwork
import random

SLOT_DURATION = 12
NUM_STAKERS = 100  # ← Cambio aquí
ZERO_HASH = '0'*64

# ... resto del código igual ...

if __name__ == '__main__':
    # ... código genesis ...

    network = P2PNetwork(latency_func)
    stakers = [Staker(i, network, genesis_block, genesis_state)
               for i in range(NUM_STAKERS)]

    print(f"Simulando {NUM_STAKERS} validadores...")

    for time in range(2000):  # Más tiempo para convergencia
        network.time_step()
        for staker in stakers:
            staker.tick()

        if time % (SLOT_DURATION * 10) == 0:  # Print cada 10 slots
            print(f"Time {time}: Slot {time // SLOT_DURATION + 2}")
```

**Ejecutar:**
```bash
python3 simulate_large.py
```

---

### Ejemplo 5: Latencia Variable Realista

**Archivo:** `latency_profiles.py`
```python
import random

# Perfil 1: Latencia normal con picos ocasionales
def realistic_latency(t):
    if random.random() < 0.05:  # 5% de probabilidad
        return int(SLOT_DURATION * 3)  # Spike de 3 slots
    else:
        return int(SLOT_DURATION * 0.3 * random.random())  # 0-3.6s

# Perfil 2: Red empeorando con el tiempo
def degrading_latency(t):
    base = 1 + (t / 1000) * 20  # Crece de 1 a 20
    return int(base + random.random() * 10)

# Perfil 3: Red mejorando con el tiempo
def improving_latency(t):
    base = 20 - (t / 1000) * 19  # Decrece de 20 a 1
    return max(1, int(base + random.random() * 5))

# Usar en simulate.py:
network = P2PNetwork(realistic_latency)
```

---

## 🦹 Agregar Validadores Bizantinos

### Ejemplo 6: Validador que Vota Aleatoriamente

**Agregar al final de `p2p.py`:**
```python
class RandomVoterStaker(Staker):
    """Validador bizantino que vota por bloques aleatorios"""

    def vote(self):
        state = self.post_states[self.head]

        # Elegir un bloque aleatorio en lugar del head correcto
        random_blocks = list(self.chain.keys())
        if not random_blocks:
            return

        random_head = random.choice(random_blocks)
        target_block = self.chain[random_head]

        # Usar target aleatorio también
        random_target = random.choice(random_blocks)
        target_block = self.chain[random_target]

        vote = Vote(
            validator_id=self.validator_id,
            slot=self.get_current_slot(),
            head=random_head,
            head_slot=self.chain[random_head].slot,
            target=random_target,
            target_slot=target_block.slot,
            source=state.latest_justified_hash,
            source_slot=state.latest_justified_slot
        )

        self.receive(vote)
        self.network.submit(vote, self.validator_id)

        print(f"⚠️  Byzantine Staker {self.validator_id} voted randomly!")
```

**Usar en `simulate.py`:**
```python
# Importar
from p2p import Staker, P2PNetwork, RandomVoterStaker

# Crear validadores (9 honestos + 1 bizantino)
stakers = []
for i in range(9):
    stakers.append(Staker(i, network, genesis_block, genesis_state))

# Último validador es bizantino
stakers.append(RandomVoterStaker(9, network, genesis_block, genesis_state))

print("⚠️  Validador 9 es BIZANTINO (vota aleatoriamente)")
```

---

### Ejemplo 7: Validador que Siempre Vota Tarde

**Agregar a `p2p.py`:**
```python
class SlowStaker(Staker):
    """Validador que siempre responde con delay adicional"""

    def __init__(self, validator_id, network, genesis_block, genesis_state,
                 extra_delay=SLOT_DURATION):
        super().__init__(validator_id, network, genesis_block, genesis_state)
        self.extra_delay = extra_delay
        self.delayed_actions = []  # Cola de acciones pendientes

    def vote(self):
        # Guardar el voto para después
        self.delayed_actions.append((self.network.time + self.extra_delay, 'vote'))

    def tick(self):
        # Procesar acciones retrasadas
        current_time = self.network.time
        actions_to_do = [a for t, a in self.delayed_actions if t <= current_time]
        self.delayed_actions = [(t, a) for t, a in self.delayed_actions if t > current_time]

        for action in actions_to_do:
            if action == 'vote':
                super().vote()  # Ejecutar voto con delay

        # Llamar tick normal
        super().tick()
```

---

## 🌐 Simular Particiones de Red

### Ejemplo 8: Split de Red Temporal

**Crear `partition_network.py`:**
```python
from p2p import P2PNetwork
from collections import defaultdict

class PartitionedNetwork(P2PNetwork):
    """Red que puede dividirse en particiones"""

    def __init__(self, latency_func):
        super().__init__(latency_func)
        self.partition_start = None
        self.partition_end = None
        self.partition_groups = []  # [[0,1,2,3,4], [5,6,7,8,9]]

    def set_partition(self, start_time, end_time, groups):
        """Configurar partición de red"""
        self.partition_start = start_time
        self.partition_end = end_time
        self.partition_groups = groups

    def submit(self, item, sender_id):
        current_time = self.time

        # Verificar si estamos en período de partición
        if (self.partition_start and self.partition_end and
            self.partition_start <= current_time < self.partition_end):

            # Encontrar grupo del sender
            sender_group = None
            for group in self.partition_groups:
                if sender_id in group:
                    sender_group = group
                    break

            # Solo enviar a validadores del mismo grupo
            for recipient_id in sender_group:
                if recipient_id == sender_id:
                    continue
                deliver_at = self.time + self.latency_func(self.time)
                self.queues[recipient_id].append((deliver_at, item))
        else:
            # Comportamiento normal
            super().submit(item, sender_id)

# Uso en simulate.py:
network = PartitionedNetwork(latency_func)

# Crear split: validadores 0-4 vs 5-9 entre tiempo 300-600
network.set_partition(
    start_time=300,
    end_time=600,
    groups=[[0,1,2,3,4], [5,6,7,8,9]]
)

print("⚠️  Network partition: t=300-600, grupos [0-4] vs [5-9]")
```

---

## 📊 Análisis de Datos

### Ejemplo 9: Extraer Métricas

**Crear `analyze_logs.py`:**
```python
import re
import sys
from collections import defaultdict

def analyze_simulation_log(log_file):
    """Analiza un log de simulación y extrae métricas"""

    finalized_by_time = []
    justified_by_time = []
    convergence_by_slot = defaultdict(list)

    with open(log_file, 'r') as f:
        current_time = None
        current_slot = None

        for line in f:
            # Extraer tiempo y slot
            time_match = re.search(r'=== Time (\d+) \(Slot (\d+)\)', line)
            if time_match:
                current_time = int(time_match.group(1))
                current_slot = int(time_match.group(2))

            # Extraer estado de validadores
            staker_match = re.search(
                r'Staker (\d+): Head=\w+ \(slot\s+(\d+)\) \| '
                r'Justified=\w+ \(slot\s+(\d+)\) \| '
                r'Finalized=\w+ \(slot\s+(\d+)\)',
                line
            )
            if staker_match and current_time and current_slot:
                staker_id = int(staker_match.group(1))
                head_slot = int(staker_match.group(2))
                justified_slot = int(staker_match.group(3))
                finalized_slot = int(staker_match.group(4))

                convergence_by_slot[current_slot].append(head_slot)

                if staker_id == 0:  # Trackear Staker 0 como referencia
                    finalized_by_time.append((current_time, finalized_slot))
                    justified_by_time.append((current_time, justified_slot))

    # Calcular métricas
    print("📊 Análisis de Simulación")
    print("=" * 50)

    # Finality lag promedio
    finality_lags = []
    for time, fin_slot in finalized_by_time:
        current_slot = time // 12 + 2
        lag = current_slot - fin_slot
        finality_lags.append(lag)

    print(f"\n🔹 Finality Lag:")
    print(f"   Promedio: {sum(finality_lags)/len(finality_lags):.2f} slots")
    print(f"   Mínimo: {min(finality_lags)} slots")
    print(f"   Máximo: {max(finality_lags)} slots")

    # Convergencia
    print(f"\n🔹 Convergencia de Heads:")
    perfect_convergence = 0
    for slot, heads in convergence_by_slot.items():
        if len(set(heads)) == 1:  # Todos en el mismo head
            perfect_convergence += 1

    total_slots = len(convergence_by_slot)
    print(f"   Slots con convergencia perfecta: {perfect_convergence}/{total_slots}")
    print(f"   Porcentaje: {100*perfect_convergence/total_slots:.1f}%")

    # Progreso de finality
    print(f"\n🔹 Progreso de Finality:")
    if len(finalized_by_time) > 10:
        early = finalized_by_time[10][1]
        late = finalized_by_time[-1][1]
        time_elapsed = finalized_by_time[-1][0] - finalized_by_time[10][0]
        slots_finalized = late - early

        print(f"   Slots finalizados: {slots_finalized}")
        print(f"   Tiempo transcurrido: {time_elapsed} time units")
        print(f"   Tasa: {slots_finalized / (time_elapsed/12):.2%} (slots fin / slots totales)")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 analyze_logs.py <log_file>")
        sys.exit(1)

    analyze_simulation_log(sys.argv[1])
```

**Uso:**
```bash
python3 simulate.py > my_sim.log
python3 analyze_logs.py my_sim.log
```

---

## 🎨 Visualización

### Ejemplo 10: Graficar Finality Progress

**Crear `plot_metrics.py`:**
```python
import re
import matplotlib.pyplot as plt
import sys

def plot_finality_progress(log_file):
    """Grafica el progreso de finalización"""

    times = []
    finalized_slots = []
    justified_slots = []
    head_slots = []

    with open(log_file, 'r') as f:
        for line in f:
            # Buscar líneas de Staker 0
            match = re.search(
                r'=== Time (\d+).*\n.*Staker 0: Head=\w+ \(slot\s+(\d+)\) \| '
                r'Justified=\w+ \(slot\s+(\d+)\) \| Finalized=\w+ \(slot\s+(\d+)\)',
                line + next(f, '')
            )
            if match:
                times.append(int(match.group(1)))
                head_slots.append(int(match.group(2)))
                justified_slots.append(int(match.group(3)))
                finalized_slots.append(int(match.group(4)))

    # Crear gráfico
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Gráfico 1: Progreso de slots
    ax1.plot(times, head_slots, label='Head', linewidth=2)
    ax1.plot(times, justified_slots, label='Justified', linewidth=2)
    ax1.plot(times, finalized_slots, label='Finalized', linewidth=2)
    ax1.set_xlabel('Time (units)')
    ax1.set_ylabel('Slot Number')
    ax1.set_title('3SF Consensus Progress')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Gráfico 2: Lag (distancia del head)
    current_slots = [t // 12 + 2 for t in times]
    finality_lag = [c - f for c, f in zip(current_slots, finalized_slots)]
    justified_lag = [c - j for c, j in zip(current_slots, justified_slots)]

    ax2.plot(times, finality_lag, label='Finality Lag', linewidth=2, color='red')
    ax2.plot(times, justified_lag, label='Justified Lag', linewidth=2, color='orange')
    ax2.set_xlabel('Time (units)')
    ax2.set_ylabel('Lag (slots)')
    ax2.set_title('Consensus Lag Over Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('finality_progress.png', dpi=150)
    print("📊 Gráfico guardado: finality_progress.png")
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 plot_metrics.py <log_file>")
        print("Requiere: pip install matplotlib")
        sys.exit(1)

    plot_finality_progress(sys.argv[1])
```

**Uso:**
```bash
pip install matplotlib
python3 simulate.py > sim.log
python3 plot_metrics.py sim.log
```

---

## 🧪 Experimentos Automatizados

### Ejemplo 11: Benchmark Suite

**Crear `benchmark.sh`:**
```bash
#!/bin/bash

echo "🧪 3SF-mini Benchmark Suite"
echo "============================"

mkdir -p benchmarks

# Test 1: Latencia variable
echo "Test 1: Comparar latencias..."
for latency in 1 5 10 20; do
    echo "  Latencia = $latency"
    # Modificar simulate.py automáticamente
    sed "s/return 1/return $latency/" simulate.py > temp_sim.py
    python3 temp_sim.py > benchmarks/latency_${latency}.log
done

# Test 2: Escalar validadores
echo "Test 2: Escalar validadores..."
for n in 10 20 50 100; do
    echo "  $n validadores"
    sed "s/NUM_STAKERS = 10/NUM_STAKERS = $n/" simulate.py > temp_sim.py
    timeout 60 python3 temp_sim.py > benchmarks/validators_${n}.log || echo "Timeout"
done

rm temp_sim.py

echo "✅ Benchmarks completados en: benchmarks/"
```

---

## 💡 Tips y Trucos

### Ver convergencia en tiempo real
```bash
python3 simulate.py | while read line; do
    echo "$line"
    if [[ $line == *"Slot"* ]]; then
        sleep 0.5  # Pausa para ver mejor
    fi
done
```

### Extraer solo slots finalizados
```bash
python3 simulate.py | grep "Finalized" | awk '{print $NF}' | sort -u
```

### Comparar dos simulaciones
```bash
diff -y <(python3 sim1.py | grep "Estado Final") \
        <(python3 sim2.py | grep "Estado Final")
```

---

Para más ejemplos, revisa:
- **README.md** - Guía completa
- **ANALISIS_SIMULACION.md** - Análisis detallado
- **Código fuente** - `consensus.py`, `p2p.py`, `simulate.py`

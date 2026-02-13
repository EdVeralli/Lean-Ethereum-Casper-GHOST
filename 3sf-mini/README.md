# 3SF-mini: Simulador de 3-Slot Finality

Implementación de referencia del protocolo **3-Slot Finality (3SF)** de Ethereum Research, el futuro mecanismo de consenso de Ethereum que reduce el tiempo de finalidad de **12.8 minutos a ~12 segundos**.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración Avanzada](#configuración-avanzada)
- [Ejemplos](#ejemplos)
- [Troubleshooting](#troubleshooting)
- [Referencias](#referencias)

---

## 🎯 Descripción

Este simulador implementa el protocolo **3SF-mini** (~200 líneas de Python), que incluye:

- ✅ **LMD GHOST:** Fork choice rule basado en últimos votos de validadores
- ✅ **Backoff Technique:** Justificación progresiva incluso con alta latencia
- ✅ **Safe Target:** Garantía de seguridad con supermayoría 2/3
- ✅ **View Merge:** Sincronización de attestations entre validadores
- ✅ **P2P Network Simulation:** Simulador de latencia de red configurable

**Repositorio oficial:** [ethereum/research/3sf-mini](https://github.com/ethereum/research/tree/master/3sf-mini)

---

## 📦 Requisitos

### Requisitos Mínimos

- **Python:** 3.8 o superior
- **Sistema Operativo:** Linux, macOS, o Windows
- **Memoria RAM:** 512 MB (para 10 validadores)

### Dependencias

El simulador básico **NO requiere dependencias externas**. Solo usa la biblioteca estándar de Python:
- `dataclasses` (Python 3.7+)
- `hashlib`
- `json`
- `copy`
- `random`
- `typing`
- `collections`

#### Opcional (para visualización)

Si quieres visualizar el árbol de bloques:
```bash
pip install matplotlib networkx
```

---

## 🚀 Instalación

### Opción 1: Clonar solo 3sf-mini

```bash
# Si ya tienes este repositorio
cd Lean-Ethereum-Casper-GHOST/3sf-mini

# Verificar instalación de Python
python3 --version  # Debe ser >= 3.8
```

### Opción 2: Desde cero

```bash
# Crear directorio
mkdir 3sf-mini && cd 3sf-mini

# Descargar archivos desde ethereum/research
curl -O https://raw.githubusercontent.com/ethereum/research/master/3sf-mini/consensus.py
curl -O https://raw.githubusercontent.com/ethereum/research/master/3sf-mini/p2p.py
curl -O https://raw.githubusercontent.com/ethereum/research/master/3sf-mini/test_p2p.py
```

O usa los archivos incluidos en este repositorio (ya están listos).

---

## ⚡ Uso Rápido

### Ejecutar la simulación básica

```bash
cd 3sf-mini
python3 simulate.py
```

**Salida esperada:**
```
=== Simulación 3SF-mini iniciada ===
Validadores: 10
Slot duration: 12s
Latencia: Alta (t<667) → Baja (t≥667)

=== Time 0 (Slot 2) ===
Staker 0: Head=bd7dc661 (slot   1) | Justified=00000000 (slot   0) | Finalized=00000000 (slot   0)
...

=== Time 996 (Slot 85) ===
Staker 0: Head=ef5f9591 (slot  85) | Justified=5f5ffc18 (slot  83) | Finalized=00a61e52 (slot  82)
...

=== Simulación completada ===
Total bloques en cadena: 84
Total votos conocidos: 830
Último slot finalizado: 82
Último slot justificado: 83
```

**Tiempo de ejecución:** ~5-10 segundos en hardware moderno

---

## 📂 Estructura del Proyecto

```
3sf-mini/
├── README.md                    # Este archivo
├── ANALISIS_SIMULACION.md      # Análisis detallado de resultados
├── consensus.py                 # Core del protocolo 3SF (~200 líneas)
│   ├── Config, State, Vote, Block (dataclasses)
│   ├── is_justifiable_slot()   # Backoff technique
│   ├── process_block()          # Procesar votos y actualizar estado
│   └── get_fork_choice_head()   # LMD GHOST fork choice
├── p2p.py                       # Capa de red y validadores
│   ├── Staker                   # Implementación de validador
│   │   ├── propose_block()      # Proponer bloques (t=0)
│   │   ├── vote()               # Emitir votos (t=3s)
│   │   ├── compute_safe_target() # Calcular target seguro (t=6s)
│   │   └── accept_new_votes()   # View merge (t=9s)
│   └── P2PNetwork               # Simulador de red con latencia
└── simulate.py                  # Script principal de simulación
```

### Flujo de Datos

```
Genesis Block → P2PNetwork → Staker[0..9]
                    ↓
              [Latency Simulation]
                    ↓
        Staker.tick() every second
                    ↓
    t=0: propose_block() (si es su turno)
    t=3: vote() (todos)
    t=6: compute_safe_target() (todos)
    t=9: accept_new_votes() (todos)
                    ↓
        process_block() → State updates
                    ↓
        get_fork_choice_head() → Convergencia
```

---

## ⚙️ Configuración Avanzada

### Modificar Parámetros de Simulación

Edita `simulate.py`:

```python
# Línea 7-8: Configuración básica
SLOT_DURATION = 12      # Duración del slot en segundos (default: 12)
NUM_STAKERS = 10        # Número de validadores (default: 10)

# Línea 31-34: Función de latencia
def latency_func(t):
    if t < 667:
        # Alta latencia: hasta 2.5 slots de delay
        return int(SLOT_DURATION * 2.5 * random.random() ** 3)
    else:
        # Baja latencia: 1 time unit de delay
        return 1

# Línea 45: Duración de la simulación
for time in range(1000):  # Cambiar 1000 por otro valor
```

### Ejemplos de Configuración

#### 1. Simular Red Real (100 validadores)

```python
NUM_STAKERS = 100
```

**Nota:** Incrementa el tiempo de ejecución a ~30-60 segundos.

#### 2. Latencia Constante Baja

```python
def latency_func(t):
    return 1  # Siempre 1 time unit
```

#### 3. Latencia Variable Realista

```python
import random

def latency_func(t):
    # Simular picos de latencia aleatorios
    if random.random() < 0.05:  # 5% de probabilidad
        return int(SLOT_DURATION * 5)  # Spike de 5 slots
    else:
        return int(SLOT_DURATION * 0.5 * random.random())  # 0-6s normal
```

#### 4. Simulación Más Larga (500 slots)

```python
for time in range(6000):  # 500 slots * 12s = 6000 time units
```

---

## 🧪 Ejemplos

### Ejemplo 1: Simulación Básica

```bash
python3 simulate.py
```

### Ejemplo 2: Aumentar Validadores

```bash
# Editar simulate.py línea 8
# NUM_STAKERS = 50

python3 simulate.py > output_50_validators.txt
tail -20 output_50_validators.txt  # Ver resultados finales
```

### Ejemplo 3: Guardar Logs Completos

```bash
python3 simulate.py > logs/simulation_$(date +%Y%m%d_%H%M%S).log 2>&1
```

### Ejemplo 4: Ver Solo Slots Clave

```bash
python3 simulate.py | grep "=== Time"
```

### Ejemplo 5: Analizar Convergencia

```bash
python3 simulate.py | grep "Slot 60" | head -10
```

---

## 🔧 Troubleshooting

### Problema: `ModuleNotFoundError: No module named 'consensus'`

**Solución:**
```bash
# Asegúrate de estar en el directorio correcto
cd 3sf-mini

# Verifica que los archivos existan
ls -la *.py
# Debes ver: consensus.py, p2p.py, simulate.py
```

### Problema: `python: command not found`

**Solución:**
```bash
# Intenta con python3
python3 simulate.py

# O verifica la instalación
which python3
```

### Problema: Simulación muy lenta (>60 segundos)

**Causa:** Demasiados validadores o tiempo de simulación muy largo

**Solución:**
```python
# Reducir en simulate.py
NUM_STAKERS = 10  # En lugar de 100+
for time in range(1000):  # En lugar de 10000+
```

### Problema: Validadores no convergen

**Causa:** Latencia demasiado alta o función de latencia incorrecta

**Solución:**
```python
# Probar con latencia constante baja
def latency_func(t):
    return 1
```

### Problema: `AssertionError` en `is_justifiable_slot()`

**Causa:** Bug en modificaciones personalizadas del código

**Solución:** Restaura los archivos originales desde este repositorio o desde [ethereum/research](https://github.com/ethereum/research/tree/master/3sf-mini).

---

## 🧠 Entendiendo la Salida

### Formato de Output

```
Staker 0: Head=bd7dc661 (slot   1) | Justified=00000000 (slot   0) | Finalized=00000000 (slot   0)
          ↑    ↑         ↑           ↑          ↑          ↑          ↑           ↑
          ID   Hash      Slot        Estado     Hash       Slot       Estado      Slot
```

- **Head:** Bloque que el validador considera como cabeza de la cadena (LMD GHOST)
- **Justified:** Bloque que ha recibido 2/3 de votos (checkpoint)
- **Finalized:** Bloque irreversible (2 justifications consecutivas)

### Métricas Clave

```
=== Estado Final ===
Total bloques en cadena: 84        # Número de bloques creados
Total votos conocidos: 830         # Número de votos emitidos (≈10 por bloque)
Último slot finalizado: 82         # Slot con finalidad
Último slot justificado: 83        # Slot con 2/3 de votos
```

**Slots justificados pero no finalizados:** 1 slot (83 - 82)
**Latencia de finalidad:** ~2-3 slots en condiciones normales

---

## 📊 Análisis de Resultados

Después de ejecutar la simulación, revisa:

```bash
# Ver análisis detallado
cat ANALISIS_SIMULACION.md

# Buscar eventos clave
grep "Finalized" logs/simulation.log | tail -20  # Últimas finalizaciones
```

**Métricas importantes:**
- **Convergencia:** ¿Todos los validadores tienen el mismo head?
- **Finality gap:** Diferencia entre slot actual y slot finalizado
- **Justification gap:** Diferencia entre slot actual y slot justificado

---

## 🎓 Experimentos Sugeridos

### 1. Comparar Alta vs Baja Latencia

```bash
# Alta latencia constante
# def latency_func(t): return 30
python3 simulate.py > high_latency.log

# Baja latencia constante
# def latency_func(t): return 1
python3 simulate.py > low_latency.log

# Comparar finality
grep "Estado Final" high_latency.log low_latency.log
```

### 2. Escalar Número de Validadores

```bash
for n in 10 20 50 100; do
    # Editar NUM_STAKERS = $n
    python3 simulate.py > results_${n}_validators.log
done
```

### 3. Agregar Validador Bizantino

Edita `p2p.py`:

```python
class ByzantineStaker(Staker):
    """Validador malicioso que vota aleatoriamente"""
    def vote(self):
        import random
        state = self.post_states[self.head]
        # Elegir un bloque aleatorio en lugar del head correcto
        random_hash = random.choice(list(self.chain.keys()))
        target_block = self.chain[random_hash]
        # ... resto del código de vote() con target_block
```

En `simulate.py`:

```python
# Crear 9 honestos + 1 bizantino
stakers = [Staker(i, network, genesis_block, genesis_state) for i in range(9)]
stakers.append(ByzantineStaker(9, network, genesis_block, genesis_state))
```

---

## 📚 Referencias

### Papers

- **3-Slot Finality (2024):** [arXiv:2411.00558](https://arxiv.org/abs/2411.00558)
- **Single Slot Finality (2023):** [arXiv:2302.12745](https://arxiv.org/abs/2302.12745)
- **Gasper (2020):** [arXiv:2003.03052](https://arxiv.org/abs/2003.03052)
- **Model Checking 3SF:** [arXiv:2501.07958](https://arxiv.org/abs/2501.07958)

### Recursos

- **Repositorio oficial:** [ethereum/research/3sf-mini](https://github.com/ethereum/research/tree/master/3sf-mini)
- **Lean Roadmap:** [leanroadmap.org](https://leanroadmap.org/)
- **Blog post de Justin Drake:** [blog.ethereum.org/2025/07/31/lean-ethereum](https://blog.ethereum.org/2025/07/31/lean-ethereum)
- **Verificación formal (TLA+):** [freespek/ssf-mc](https://github.com/freespek/ssf-mc)

### Clientes en Desarrollo

- [lambdaclass/ethlambda](https://github.com/lambdaclass/ethlambda) (Rust)
- [ReamLabs/ream](https://github.com/ReamLabs/ream) (Rust)
- [blockblaz/zeam](https://github.com/blockblaz/zeam) (Zig)
- [qdrvm/qlean](https://github.com/qdrvm) (C++)

---

## 🤝 Contribuciones

Este código es parte de **Ethereum Research** y está destinado a fines educativos y de investigación.

Para contribuir:
1. Forkea el repositorio original
2. Experimenta y reporta findings
3. Abre issues o PRs en [ethereum/research](https://github.com/ethereum/research)

---

## 📄 Licencia

Este código sigue la licencia del repositorio [ethereum/research](https://github.com/ethereum/research) (MIT License).

---

## 📧 Contacto

- **Ethereum Research:** lean@ethereum.org
- **Issues:** [github.com/ethereum/research/issues](https://github.com/ethereum/research/issues)
- **Discusión:** [ethresear.ch](https://ethresear.ch/)

---

**¡Happy simulating!** 🚀

Si encuentras bugs o tienes sugerencias, abre un issue en el repositorio.

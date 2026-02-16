# Lean Consensus y el Protocolo 3-Slot Finality (3SF)

## Estudio tecnico completo del protocolo de consenso propuesto para Ethereum

---

## 1. Origen y evolucion

### De SSF a 3SF

El protocolo **3-Slot Finality (3SF)** es la evolucion practica del protocolo **Single Slot Finality (SSF)** propuesto por D'Amato y Zanolini en 2023.

| Fecha | Hito |
|---|---|
| Feb 2023 | D'Amato & Zanolini publican **SSF** — Single Slot Finality ([arXiv:2302.12745](https://arxiv.org/abs/2302.12745)) |
| Nov 2024 | Justin Drake presenta **"Beam Chain"** en Devcon Bangkok |
| Nov 2024 | D'Amato, Saltini, Tran & Zanolini publican **3SF** ([arXiv:2411.00558](https://arxiv.org/abs/2411.00558)) |
| Jul 2025 | Drake publica **"lean Ethereum"** — renombra Beam Chain a Lean Ethereum |
| Sep 2025 | **pq-devnet-0** — primer devnet multi-cliente con 3SF-mini |
| Nov 2025 | **pq-devnet-1** — integracion de leanSig (firmas post-cuanticas) |
| Ene 2026 | **pq-devnet-2** — agregacion completa con leanMultisig |

### El problema de SSF

SSF lograba finalidad en **1 slot**, pero requeria **2 rondas de agregacion de firmas BLS** por slot (una para head votes y otra para FFG votes). Con ~1 millon de validadores en Ethereum, esto creaba un cuello de botella insostenible de ancho de banda y agregacion.

### Las 3 modificaciones de SSF a 3SF

1. **Fusion de votos:** Los FFG votes se emiten junto con los head votes en un unico mensaje a tiempo Delta del slot
2. **Eliminacion de fast-confirmations:** El target del FFG vote es la cadena mas larga confirmada por el protocolo de disponibilidad
3. **Eliminacion de Acknowledgment votes:** Se remueven los mensajes de reconocimiento para observadores externos

**Resultado:** 3SF tiene una latencia de finalidad de 3 slots (vs 1 en SSF), pero requiere solo **1 ronda de agregacion por slot** en vez de 2 — un compromiso practico que reduce a la mitad la carga de comunicacion.

---

## 2. Estructura de datos fundamental

### 2.1 Checkpoint: la triple `(B, c, p)`

A diferencia de Gasper que usa checkpoints `(Block, epoch)`, 3SF introduce una **triple**:

```
Checkpoint = (B, c, p)

  B = bloque
  c = checkpoint slot (slot donde se propone B para justificacion)
  p = proposal slot = slot(B)

  Invariante: para checkpoints no-genesis, c > p
  Genesis: (G, 0, 0)
```

Esta estructura de triple permite el pipeline de 3 slots, ya que desacopla el momento de propuesta del bloque del momento de su justificacion.

### 2.2 FFG Vote (enlace entre checkpoints)

Un FFG vote es un enlace dirigido entre dos checkpoints:

```
(B1, c1, p1) --> (B2, c2, p2)

  Source: (B1, c1, p1) — debe ser un checkpoint justificado
  Target: (B2, c2, p2) — checkpoint al que se vota

  Restricciones:
    B1 <= B2    (B1 es ancestro de B2)
    c2 > c1     (target checkpoint slot estrictamente mayor que source)
```

### 2.3 Attestation (voto fusionado)

En 3SF, una attestation es un par **(head_vote, FFG_vote)** fusionado en un solo mensaje:

```
Attestation = (B_head, J_source --> T_target)

  B_head = head vote (referencia al bloque tip de la cadena)
  J      = mayor checkpoint justificado (source del FFG vote)
  T      = target checkpoint = (C, p, slot(C))
           donde C = bloque confirmado mas alto
```

Cada attestation tiene un slot asociado — el slot en el que debe enviarse — que corresponde al checkpoint slot del target del FFG vote.

### 2.4 NodeState (equivalente al Store de Gasper)

El estado local de cada nodo validador. Contiene solo campos no-derivables:

- Todos los bloques conocidos y sus relaciones en el arbol
- Todos los FFG votes recibidos
- Conjunto de checkpoints justificados
- Conjunto de checkpoints finalizados
- Mayor checkpoint justificado (para seleccion de source del FFG vote)
- Bloque confirmado mas alto
- Conjunto de candidatos a confirmacion
- Estado de vista congelada (para view-merge a tiempo 3*Delta)
- Tracking del slot actual

En la implementacion de referencia ([fradamt/ssf](https://github.com/fradamt/ssf/tree/main/high_level)), las estructuras inmutables usan `@dataclass(frozen=True)` y las colecciones usan `PSet`, `PVector`, `PMap` de la libreria `pyrsistent`.

---

## 3. Mecanica del slot: Propose-Attest-Confirm-Freeze

Cada slot `s` sigue esta linea temporal, donde **Delta** es el limite conocido de latencia de red:

### Tiempo 0*Delta: PROPOSE

```
1. El proposer designado ejecuta el fork-choice rule para determinar el head actual
2. Propone un nuevo bloque extendiendo el output del fork-choice
3. Incluye un VIEW-MERGE MESSAGE con su mayor checkpoint justificado
4. Broadcast de la propuesta a todos los validadores
```

### Tiempo 1*Delta: MERGE + ATTEST

```
1. Los attesters realizan MERGING si es necesario:
   - Comparan su mayor checkpoint justificado con el del proposer
   - Si el del proposer es mayor, actualizan el suyo (view-merge)
2. Los attesters ejecutan el fork-choice
3. Los attesters construyen y broadcastean su attestation:

   Attest to (B, J --> T) donde:
     B = head de la cadena (del fork choice)
     J = mayor checkpoint justificado (source)
     T = target checkpoint = (C, p, slot(C))
         donde C = bloque confirmado mas alto
```

### Tiempo 2*Delta: CONFIRM (identificar candidatos a confirmacion)

```
Un nodo agrega un bloque B a su conjunto de CONFIRMATION CANDIDATES
si a tiempo 2*Delta del slot s ha recibido:
  >= 2/3 de head votes del slot s que estan en el subarbol de B

Un bloque B se considera CONFIRMED si:
  - B es la raiz del fork-choice (siempre confirmado), O
  - B es un candidato a confirmacion CANONICO
    (un candidato que esta en la cadena canonica)
```

### Tiempo 3*Delta: FREEZE (frontera de view-merge)

```
La vista se CONGELA para el view-merge.
Crea un snapshot del estado del validador que se usara
para la propuesta del siguiente slot.
Mensajes recibidos despues del freeze NO afectan la vista congelada.
```

### Arquitectura event-driven

En la especificacion ([3sf_high_level.py](https://github.com/fradamt/ssf/tree/main/high_level)), los handlers usan un patron `@Event`:

```python
@Event
def on_received_propose(node_state, propose_message):
    # Procesar propuesta entrante
    # Actualizar arbol de bloques
    # Realizar view-merge si el checkpoint del proposer es mayor
    ...

@Event
def on_tick_attest(node_state, slot):
    # A tiempo 1*Delta:
    # Merge si es necesario
    # Ejecutar fork choice
    # Construir attestation (B, J -> T)
    # Broadcast attestation
    ...

@Event
def on_received_attestation(node_state, attestation):
    # Procesar attestation entrante
    # Actualizar tracking de votos
    # Verificar candidatos a confirmacion a tiempo 2*Delta
    ...

@Event
def on_tick_freeze(node_state, slot):
    # A tiempo 3*Delta:
    # Congelar la vista para view-merge
    ...
```

---

## 4. El pipeline de 3-Slot Finality

Para un bloque propuesto por un proposer honesto en el slot `t`, la finalidad se alcanza deterministicamente:

```
                    SLOT t              SLOT t+1            SLOT t+2
                    ======              ========            ========
Proposer         → Propone bloque B

Attesters        → >= 2/3 head votes   → FFG votes con     → FFG votes con
                    en subarbol de B      source justificado   source = checkpoint
                                          apuntando a B        recien justificado

Resultado        → B es CONFIRMED      → Checkpoint         → Checkpoint
                                          (B, t+1, t) es       (B, t+1, t) es
                                          JUSTIFIED             FINALIZED

Tiempo total: 3 slots x ~4 segundos = ~12 segundos
```

### Paso a paso

**Slot t — Confirmacion:**
- Proposer honesto propone bloque B
- A tiempo 2*Delta, validadores honestos reciben >= 2/3 head votes en el subarbol de B
- B se convierte en candidato a confirmacion
- Como todos los validadores honestos ven B como canonico, B es **CONFIRMED**

**Slot t+1 — Justificacion:**
- Los attesters en slot t+1 usan B como parte de su target checkpoint
- Todos los >= 2/3 attestations honestos del slot t tienen el mismo source checkpoint
- Un attestation honesto en slot t+1 tiene source `(B', t, slot(B'))` donde B' es predecesor de B
- El checkpoint `T = (B, t+1, t)` es **JUSTIFIED** por todos los validadores honestos

**Slot t+2 — Finalizacion:**
- Los attesters en slot t+2 usan el checkpoint recien justificado `(B, t+1, t)` como source
- Con >= 2/3 votos honestos enlazando desde este source al siguiente target
- El checkpoint `T = (B, t+1, t)` es **FINALIZED** por todos los validadores honestos

### Propiedad critica

> Este pipeline funciona **independientemente de si los proposers de los slots t+1 y t+2 son honestos**, siempre que se mantenga sincronia y al menos 2/3 de los participantes sean honestos y activos hasta la ronda de votos del slot t+2.

---

## 5. Reglas de justificacion y finalizacion (formal)

### 5.1 Justificacion

Un checkpoint `(B, c, p)` esta **justificado** si y solo si:

```
CASO 1: Es el genesis (G, 0, 0)

CASO 2: Existe un conjunto de >= 2/3 FFG votes de la forma:

  (A_i, c_i, p_i) --> (B_i, c, p_i')

  satisfaciendo:
    A_i <= B <= B_i    para todos los votos
                       (todos los source blocks son ancestros de B,
                        y B es ancestro de todos los target blocks)

    Todos los source checkpoints (A_i, c_i, p_i) estan justificados

    El target checkpoint slot "c" es el mismo en todos los votos del conjunto
```

### 5.2 Finalizacion

Un checkpoint `(B, c, p)` esta **finalizado** si y solo si:

```
1. Esta justificado, Y

2. Existe un conjunto de >= 2/3 FFG votes con:
     Source: (B, c, p)              -- el checkpoint mismo
     Target checkpoint slot: c + 1  -- el siguiente slot consecutivo
```

La finalizacion ocurre un slot despues de la justificacion, cuando un enlace de supermayoria conecta desde el checkpoint justificado al slot inmediatamente siguiente.

### 5.3 Supermajority link (definicion formal)

```
Un enlace de supermayoria A -> B existe si y solo si:

  sum(balance(v) para v en validators donde v.source == A AND v.target == B)
    >= (2/3) * total_active_balance
```

---

## 6. Fork Choice: LMD-GHOST modificado con View-Merge

### 6.1 Algoritmo `get_head` / `get_fork_choice_head`

3SF usa un **LMD-GHOST modificado**:

```
function get_head(store):
    1. INICIO: desde la raiz del fork-choice
       (el bloque del checkpoint justificado mas alto)

    2. RECORRER el arbol de bloques slot por slot (no saltar a hijos)

    3. En cada slot, calcular el HIJO MAS PESADO (best_child):
       - Pesar cada hijo por los votos de attestation en su subarbol
       - Solo contar el ULTIMO mensaje de cada validador (propiedad LMD)

    4. Comparar best_child contra empty_slot_weight:
       - Peso de "no tener bloque en este slot" (skip slot)

    5. Seleccionar la rama con mayor peso
       - Empates se rompen lexicograficamente (por hash del bloque)

    6. Continuar hasta llegar a una hoja → este es el CHAIN HEAD
```

### 6.2 View-Merge (reemplazo del Proposer Boost)

En Gasper, el **proposer boost** es un mecanismo ad-hoc que otorga un 40% de peso extra al bloque del proposer actual para mitigar ataques de balanceo y reorg. 3SF lo reemplaza con un mecanismo principiado: **view-merge**.

```
PROPOSER BOOST (Gasper) — mecanismo ad-hoc:
  El bloque del proposer recibe +40% de peso temporal en el fork choice.
  Problema: no elimina completamente los vectores de ataque.

VIEW-MERGE (3SF) — mecanismo principiado:
  1. El proposer incluye su mayor checkpoint justificado en la propuesta
  2. A tiempo 1*Delta, los attesters comparan:
     Si el del proposer es mayor → actualizan el suyo (merge)
  3. Todos los attesters honestos parten de una VISTA CONSISTENTE
  4. A tiempo 3*Delta, la vista se CONGELA
     → no mas actualizaciones hasta el siguiente slot
```

**Resultado:** Todos los attesters honestos en un slot parten de la misma vista, eliminando la superficie de ataque que el proposer boost intentaba cubrir.

---

## 7. Slashing conditions

### 7.1 E1: No Double Vote (heredada de Casper FFG)

```
Un validador NO puede emitir dos FFG votes DISTINTOS
con el MISMO target checkpoint slot.

Formalmente:
  Para todo validador v:
    NO EXISTEN votes v1, v2 tales que:
      v1 != v2 AND v1.target.c == v2.target.c

Si un validador produce votes (S1 -> T1) y (S2 -> T2)
donde T1.checkpoint_slot == T2.checkpoint_slot pero los votes difieren:
  → SLASHABLE
```

### 7.2 E2: No Surround Vote (heredada de Casper FFG)

```
Un validador NO puede emitir un voto que "rodee" un voto anterior,
ni un voto que sea "rodeado" por uno anterior.

Formalmente:
  Para todo validador v:
    NO EXISTEN votes (S1 -> T1) y (S2 -> T2) tales que:
      S2.c < S1.c AND T1.c < T2.c

Visualizacion:
  S2 <─────────────────────────────> T2    (voto externo/rodeante)
        S1 <─────────────> T1              (voto interno/rodeado)
                                           → SLASHABLE
```

### 7.3 Condicion de Monotonicidad (nueva en 3SF)

```
Los targets justificados de un validador DEBEN avanzar monotonicamente.
Un validador NUNCA puede retroceder a un checkpoint justificado anterior
como source de su FFG vote.

Formalmente:
  Si un validador emite un FFG vote con target checkpoint slot "c"
  en tiempo t1, entonces cualquier FFG vote subsiguiente en tiempo t2 > t1
  debe tener target checkpoint slot c' >= c

Implementacion local:
  - Solo actualizar el source checkpoint cuando se recibe un nuevo
    checkpoint justificado con checkpoint slot ESTRICTAMENTE mayor
  - Mantener un registro monotonicamente creciente del mayor
    checkpoint justificado usado
```

### 7.4 Por que es necesaria la condicion de monotonicidad

En Casper FFG, las dos condiciones originales (double vote + surround vote) son suficientes para accountable safety. Sin embargo, al **fusionar el head vote y el FFG vote** en 3SF, un validador podria inadvertidamente justificar **multiples checkpoints por slot**, rompiendo accountable safety.

La verificacion formal en TLA+ ([freespek/ssf-mc](https://github.com/freespek/ssf-mc)) confirmo que **sin la condicion de monotonicidad, el model checker encuentra contraejemplos inmediatamente** donde accountable safety se viola.

---

## 8. Accountable Safety Theorem

### Enunciado formal

```
Teorema (Accountable Safety):
  Si dos checkpoints conflictivos C1 y C2 son ambos finalizados,
  entonces al menos n/3 validadores adversarios pueden ser detectados
  como habiendo violado la condicion de slashing E1 o E2.

Demostracion (sketch):
  1. Finalizar C1 requiere un supermajority link: >= 2/3 del stake voto por C1
  2. Finalizar C2 (conflictivo) requiere otro supermajority link: >= 2/3 del stake
  3. Como 2/3 + 2/3 = 4/3 > 1, la interseccion contiene >= 1/3 de validadores
  4. Estos validadores necesariamente cometieron:
     - Double vote (votaron para dos targets en el mismo checkpoint slot), O
     - Surround vote (un voto rodea al otro)
  5. Ambas violaciones son criptograficamente demostrables
     y activan slashing automatico
```

### Costo economico de romper safety

```
Ethereum (estimacion 2025):
  Total staked:     ~35,700,000 ETH
  1/3 del stake:    ~11,900,000 ETH
  Precio ETH:       ~$3,700 USD
  Costo minimo:     ~$44,000,000,000 USD (~$44 mil millones)
```

### Verificacion formal

El teorema ha sido verificado formalmente por el proyecto [freespek/ssf-mc](https://github.com/freespek/ssf-mc) usando:
- **TLA+ / Apalache** — model checker simbolico
- **CVC5** — SMT solver con teoria de conjuntos finitos
- **Alloy** — cross-validacion

Verificacion exhaustiva lograda para instancias de hasta **7 checkpoints y 24 votos de validadores**.

---

## 9. Protocolo Ebb-and-Flow

3SF es un **ebb-and-flow protocol** — una arquitectura dual que combina dos sub-protocolos con propiedades complementarias:

### 9.1 Available chain (cadena disponible)

```
Sub-protocolo: Fork choice rule (LMD-GHOST modificado)
Output:        La cadena disponible (tip de la cadena)

Garantia:      LIVENESS bajo participacion dinamica
               (validadores pueden ir offline/online)

Condicion:     Requiere sincronia (mensajes llegan dentro de Delta)
               Continua progresando incluso con < 2/3 online
```

### 9.2 Finalized chain (cadena finalizada)

```
Sub-protocolo: FFG checkpoint mechanism
Output:        La cadena finalizada (prefijo irreversible)

Garantia:      SAFETY incluso bajo particiones de red
               (ningun bloque conflictivo puede finalizarse sin >= 1/3 slashing)

Condicion:     Pierde liveness bajo asincronia o cuando participacion < 2/3
```

### 9.3 Propiedades combinadas

| Propiedad | Condicion | Garantia |
|---|---|---|
| **Safety (siempre)** | — | Bloques finalizados nunca conflictan sin >= 1/3 slashing |
| **Available liveness** | Sincronia + mayoria honesta | La cadena siempre crece |
| **Finalized liveness** | Sincronia + >= 2/3 honestos y activos | Finalizacion dentro de 3 slots |
| **Latencia de finalidad** | Proposer honesto en slot t | Bloque finalizado al final del slot t+2 |

### 9.4 Composicion con protocolos DA

El paper de 3SF ([arXiv:2411.00558](https://arxiv.org/abs/2411.00558)) demuestra como integrar el gadget de finalidad 3SF con dos protocolos de consenso dinamicamente disponibles:

- **RLMD-GHOST** (Reorg-Resilient LMD-GHOST)
- **Goldfish** (protocolo sleepy model)

Esto proporciona:
- Safety y resistencia a reorgs de la cadena disponible incluso durante periodos acotados de asincronia
- Seguridad de la cadena finalizada bajo sincronia parcial
- Acuerdo a largo plazo entre ambas cadenas

---

## 10. Comparacion completa: Gasper vs SSF vs 3SF

### 10.1 Tabla de metricas

| Metrica | Gasper (actual) | SSF | 3SF |
|---|---|---|---|
| Latencia de finalidad | 64-95 slots (~13-19 min) | 1 slot | **3 slots (~12 seg)** |
| Rondas de votos por slot | 1 attestation (dual-purpose) | 2 (head + FFG separados) | **1 (fusionado)** |
| Agregaciones de firmas por slot | 1 | 2 | **1** |
| Tiempo esperado de confirmacion | N/A | 9 Delta | **8 Delta (~11% mejor)** |
| Tiempo esperado de finalizacion | ~768s | 11 Delta | **16 Delta (~46% mayor que SSF)** |
| Tolerancia a fallas | f < n/3 | f < n/3 | **f < n/3** |
| Estructura de checkpoint | (Block, epoch) | (Block, slot) | **(Block, c_slot, p_slot)** |
| Mecanismo anti-reorg | Proposer boost (ad-hoc) | View-merge | **View-merge** |
| Slashing conditions | 2 | 2 | **2 + monotonicidad** |
| Participacion | Comites por slot | Todos votan (2 rondas) | **Todos votan (1 ronda)** |

### 10.2 Trade-off clave

3SF tiene un **mejor** tiempo de confirmacion que SSF (8 Delta vs 9 Delta), pero un **peor** tiempo de finalizacion esperado (16 Delta vs 11 Delta). Sin embargo, al requerir solo **1 ronda de agregacion** por slot en vez de 2, reduce a la mitad la carga de comunicacion — critico para el millon de validadores de Ethereum.

### 10.3 Comparacion funcional detallada

| Dimension | Gasper | 3SF |
|---|---|---|
| Tipo de protocolo | Casper FFG + LMD-GHOST (dual) | Protocolo BFT unificado |
| Block time | 12 segundos | ~4 segundos |
| Min staking | 32 ETH | 1 ETH |
| Firmas | BLS12-381 (quantum-vulnerable) | Hash-based aggregate (quantum-safe) |
| Verificacion de estado | Re-ejecucion completa por cada nodo | Verificacion SNARK del beacon state |
| Aleatoriedad | RANDAO (susceptible a bias de 1-bit) | RANDAO + VDFs (resistente a bias) |
| Separacion builder/proposer | MEV-Boost (off-protocol, relays de confianza) | ePBS (enshrined, trustless) |
| Resistencia a censura | Limitada | FOCIL (inclusion lists en fork-choice) |
| Seguridad cuantica | Ninguna | Completa |
| Complejidad | Alta (dos sub-protocolos interactuando) | Reducida (protocolo unificado) |
| Factor de mejora | 1x | **64x finality mas rapido** |

---

## 11. Ataques conocidos y como 3SF los elimina

### 11.1 Analisis de causa raiz

Los ataques de **balancing**, **bouncing** y **avalanche** explotan la **dualidad temporal** inherente a Gasper: el ciclo de 12 segundos por slot de LMD-GHOST versus el ciclo de 384 segundos por epoca de Casper FFG.

```
GASPER:
  Ventana de ataque = 64 slots (2 epocas) entre fork choice y finalidad
  El atacante tiene ~12.8 minutos para manipular votos

3SF:
  Ventana de ataque = 3 slots (~12 segundos)
  Insuficiente para ejecutar ataques de balanceo/rebote
```

### 11.2 Taxonomia de ataques

| Ataque | Descripcion | Gasper | 3SF |
|---|---|---|---|
| **Balancing Attack** | Adversario balancea peso entre dos forks para impedir supermayoria, retrasando finalizacion indefinidamente | Parcialmente mitigado (Proposer Boost 40%) | **Eliminado**: 3SF no depende de LMD-GHOST como fork choice separado; finalidad y seleccion de cadena estan unificadas |
| **Bouncing Attack** | Checkpoint justificado "rebota" entre forks competidores a traves de epocas, impidiendo finalizacion | Mitigado con fork choice actualizado | **Eliminado**: Finalidad en 3 slots impide rebote cross-epoch; no hay fronteras de epoca que explotar |
| **Avalanche Attack** | Cascada de forks que amplifican inestabilidad, construyendo unos sobre otros a traves de epocas | Mitigado (Proposer Boost + ajustes de peso por slot) | **Eliminado**: Sin fronteras de epoca, no hay acumulacion de forks competidores |
| **Ex-ante Reorg** | Proposer del slot n+1 reorganiza intencionalmente el bloque del slot n para robar su MEV | Parcialmente mitigado (Proposer Boost) | **Drasticamente reducido**: Finalidad en segundos minimiza la ventana disponible para reorgs |
| **Long-Range Attack** | Atacante con stake historico (ya retirado) crea un fork alternativo desde el pasado distante | Weak subjectivity checkpoints | **Persistente pero mitigado**: Checkpoints cada ~12 segundos (vs ~12.8 minutos) reduce drasticamente la ventana |
| **Quantum Attack** | Computadora cuantica forja firmas BLS/ECDSA, permitiendo suplantacion de validadores | **SIN MITIGACION** en protocolo actual | **Eliminado**: Toda la criptografia reemplazada con primitivas hash-based post-cuanticas |
| **1-bit RANDAO bias** | Ultimo proposer de una epoca puede elegir no revelar su valor RANDAO para sesgar la aleatoriedad en 1 bit | Bajo impacto, aceptado como tolerable | **Eliminado**: VDFs (Verifiable Delay Functions) hacen la manipulacion imposible |
| **MEV censorship** | Block builders censuran transacciones especificas por razones competitivas o regulatorias | Solo via MEV-Boost (off-protocol) | **Mitigado**: ePBS (enshrined, trustless) + FOCIL (inclusion lists enforced by fork-choice) |

---

## 12. Lean Cryptography: leanSig y leanMultisig

### 12.1 La tesis unificadora

La criptografia hash-based es el fundamento que habilita las tres capas de Lean Ethereum. Justin Drake identifica dos megatendencias convergentes:

```
MEGATENDENCIA 1: SNARKs           MEGATENDENCIA 2: Cuantica
       |                                  |
  Los hashes son las               Los hashes son
  primitivas mas eficientes        resistentes a
  dentro de circuitos ZK           computacion cuantica
       |                                  |
       +──────────────+──────────────────+
                      |
           CRIPTOGRAFIA HASH-BASED
           = Fundamento unificador de Lean Ethereum
```

### 12.2 Transformacion criptografica completa

| Capa | Actual (vulnerable) | Lean (post-cuantico) |
|---|---|---|
| Consenso (CL) | BLS12-381 signatures | Hash-based aggregate signatures |
| Datos (DL) | KZG polynomial commitments | Hash-based DAS commitments |
| Ejecucion (EL) | EVM re-ejecucion por cada nodo | Hash-based real-time zkVMs |
| Transacciones | ECDSA signatures | Hash-based / lattice-based + account abstraction |

### 12.3 leanSig

- **Base:** XMSS (eXtended Merkle Signature Scheme) con firmas one-time Winternitz
- **Paper:** [LeanSig for Post-Quantum Ethereum, ePrint 2025/1332](https://eprint.iacr.org/2025/1332)
- **Propiedades:**
  - Quantum-resistant
  - Optimizado para verificacion SNARK
  - Key lifetime de ~8 anos
  - **Stateful** — cada par de claves puede producir un numero finito de firmas
- **Riesgo:** Errores de gestion de estado pueden llevar a reutilizacion de claves (falla catastrofica de seguridad)

### 12.4 leanMultisig

- **Problema:** Las firmas hash-based son ordenes de magnitud mas grandes que las firmas BLS
- **Solucion:** Agregacion SNARK recursiva
  1. Attestations individuales se agregan a nivel de subnet por agregadores
  2. Agregadores recursivamente combinan en SNARKs compactos
  3. Proposers realizan agregacion final a nivel de bloque
  4. Miles de firmas comprimidas en una sola prueba compacta
- **Estado:** Activamente en desarrollo, parte de pq-devnet-2 (enero 2026)

### 12.5 Hash-based vs Lattice-based

| Criterio | Hash-based | Lattice-based |
|---|---|---|
| Base de seguridad | Propiedades de funciones hash, estudiadas por decadas | Problemas de lattice, relativamente nuevos |
| SNARK-friendliness | Excelente (primitiva nativa de SNARKs) | Moderada |
| Tamano de firma | Mas grande | Mas compacto |
| Simplicidad | Muy simple | Mas complejo |
| Madurez | Decadas de criptoanalisis | Anos |
| Resistencia cuantica | Probada (reduccion formal a preimage/collision resistance) | Conjeturada |

La apuesta de Lean Ethereum: la **simplicidad y supuestos minimos** (solo necesitas que la funcion hash sea segura) superan las ventajas de tamano de otras familias.

---

## 13. Features adicionales de Lean Consensus

### 13.1 Staking minimo reducido (32 ETH → 1 ETH)

**Desafio:** Mas validadores = mas mensajes = mas overhead de comunicacion.

**Solucion:**
- **EIP-7251** (MaxEB a 2048 ETH) para consolidacion de validadores grandes
- Agregacion de firmas hash-based (mas eficiente que BLS para conjuntos masivos via SNARKs)
- Verificacion SNARK del beacon state (nodos verifican una prueba compacta, no cada attestation individual)

### 13.2 ePBS (Enshrined Proposer-Builder Separation)

```
Actual (off-protocol):
  Searchers → Builders → Relays (de confianza) → Proposers

Lean (enshrined PBS):
  Searchers → Builders → Protocolo (trustless) → Proposers
  + Inclusion Lists (FOCIL) para resistencia a censura
  + MEV burn (potencial)
```

### 13.3 FOCIL (Fork-Choice Enforced Inclusion Lists)

- Multiples validadores (no solo el proposer) contribuyen a una lista de transacciones que **deben** incluirse
- El fork choice rule **rechaza** bloques que no respetan la inclusion list
- Garantiza que ningun builder puede censurar transacciones indefinidamente
- Especificado en [EIP-7805](https://eips.ethereum.org/EIPS/eip-7805)

### 13.4 VDFs (Verifiable Delay Functions)

```
RANDAO actual:
  El ultimo proposer de una epoca puede elegir no revelar su valor
  → Sesgo de 1-bit en la aleatoriedad (ataque de baja complejidad)

RANDAO + VDF:
  El valor RANDAO pasa por un VDF que requiere tiempo fijo de computacion
  → La manipulacion se vuelve imposible
  → Aleatoriedad imparcial garantizada
```

---

## 14. Especificaciones y codigo de referencia

### 14.1 Implementaciones canonicas

| Recurso | URL | Lenguaje | Descripcion |
|---|---|---|---|
| Reference spec (EF) | [ethereum/research/3sf-mini](https://github.com/ethereum/research/tree/master/3sf-mini) | Python | Implementacion canonica (~200 lineas) |
| Spec completa del autor | [fradamt/ssf/high_level](https://github.com/fradamt/ssf/tree/main/high_level) | Python | `3sf_high_level.py`, `helpers.py`, `data_structures.py` |
| Spec escrita | [notes.ethereum.org/@fradamt/chained-3sf](https://notes.ethereum.org/@fradamt/chained-3sf) | — | Definicion formal del protocolo "chained" |

### 14.2 Verificacion formal

| Repositorio | Lenguaje | Que verifica |
|---|---|---|
| [freespek/ssf-mc](https://github.com/freespek/ssf-mc) | TLA+ / SMT / Alloy | Model checking de 3SF ([arXiv:2501.07958](https://arxiv.org/abs/2501.07958)) |
| [runtimeverification/casper-proofs](https://github.com/runtimeverification/casper-proofs) | Coq | Accountable Safety y Plausible Liveness de Casper FFG |
| [runtimeverification/beacon-chain-verification](https://github.com/runtimeverification/beacon-chain-verification) | Coq | Seguridad completa de Gasper (Safety + Liveness + Slashable Bound) |
| [Koukyosyumei/PoL](https://github.com/Koukyosyumei/PoL) | Lean 4 | Verificacion de consenso simplificado (educativo) |

### 14.3 Clientes de Lean Consensus (nueva generacion)

| Cliente | Lenguaje | Equipo | Estado |
|---|---|---|---|
| [ethlambda](https://github.com/lambdaclass/ethlambda) | Rust | LambdaClass | Activo, en pq-devnet-2 |
| [ream](https://github.com/ReamLabs/ream) | Rust | Ream Labs | Activo |
| [zeam](https://github.com/blockblaz/zeam) | Zig | Blockblaz | WIP, financiado por la EF |
| [qlean](https://github.com/qdrvm) | C++ | Quadrivium | Activo en devnets |
| [lantern](https://github.com/Pier-Two) | C | Pier Two | Activo |
| [grandine](https://github.com/grandinetech/grandine) | Rust | Grandine Tech | Produccion + colaborando con Lean |
| [lighthouse](https://github.com/sigp/lighthouse) (fork) | Rust | Sigma Prime | Fork interno para Lean |

### 14.4 Infraestructura de devnets

| Repositorio | Descripcion |
|---|---|
| [blockblaz/lean-quickstart](https://github.com/blockblaz/lean-quickstart) | Herramienta para levantar redes locales multi-cliente |
| [ReamLabs/lean-spec-tests](https://github.com/ReamLabs/lean-spec-tests) | Tests comunes para clientes de Lean Consensus |
| [ReamLabs/leanroadmap](https://github.com/ReamLabs/leanroadmap) | Tracking del progreso de investigacion |

---

## 15. Progreso de devnets

| Devnet | Fecha | Estado | Foco |
|---|---|---|---|
| **pq-devnet-0** | Sep 2025 | Completado | Coordinacion multi-cliente basica con 3SF-mini |
| **pq-devnet-1** | Nov 2025 | Completado | Firma y verificacion leanSig integrada en clientes |
| **pq-devnet-2** | Ene 2026 | En progreso | Agregacion completa usando leanMultisig |
| **pq-devnet-3** | TBD 2026 | Planificado | Desacoplar agregacion de produccion de bloques; rol de agregador separado |
| **pq-devnet-4** | TBD 2026 | Planificado | Agregacion recursiva a nivel de proposer |

### Plan 2026

Documentado en [Lean Consensus: 2026 Plan](https://hackmd.io/@tcoratger/ryS1ElrWbx):

- Lanzamientos de devnet **mensuales**
- Devnet de larga duracion (> 1 mes) con **10,000 validadores**
- Interoperabilidad multi-cliente con **al menos 5 implementaciones distintas**
- Validacion de topologia P2P y latencias de propagacion
- Optimizacion para slot times de 4 segundos

---

## 16. Problemas abiertos y limitaciones

### Tecnicos

1. **Cuello de botella de agregacion de firmas:** Incluso con 1 ronda por slot, agregar firmas de ~1M validadores dentro de un slot de 4 segundos es un desafio de ingenieria no resuelto

2. **Tiempo de finalizacion vs SSF:** El tiempo esperado de finalizacion de 3SF es ~46% mayor que SSF (16 Delta vs 11 Delta). Este es el costo de la simplificacion practica

3. **Complejidad de integracion:** Combinar 3SF con ePBS, FOCIL y PeerDAS introduce restricciones de timing de slot que aun se estan definiendo ([ethresear.ch/t/22909](https://ethresear.ch/t/integrating-3sf-with-epbs-focil-and-peerdas/22909))

4. **Firmas stateful:** Las firmas XMSS de leanSig son stateful — los validadores deben trackear que claves one-time han usado. Errores de gestion de estado pueden llevar a reutilizacion de claves, que es una falla catastrofica

5. **Slots de 4 segundos:** Reducir de 12s a 4s tensiona los requisitos de latencia de red y podria afectar descentralizacion si se excluyen nodos con mala conectividad

6. **Madurez de SNARK/zkVM:** Todo el esquema de agregacion depende de tecnologia SNARK y zkVM que aun esta evolucionando rapidamente

### Gaps de verificacion formal

7. **Verificacion limitada a instancias pequenas:** TLA+ model checking solo cubre instancias de hasta 7 checkpoints y 24 votos. Verificacion completa es intratable computacionalmente

8. **No existe formalizacion en Lean 4** de Casper FFG, LMD-GHOST ni Gasper. Las pruebas formales existentes usan Coq y TLA+

9. **Liveness no verificada formalmente:** El enfoque principal del model checking fue accountable safety; liveness bajo adversario no fue el foco

10. **Composicion ebb-and-flow no verificada completamente:** La verificacion formal de la composicion completa (3SF + RLMD-GHOST o Goldfish) no fue intentada

### Estandarizacion

11. **No existe EIP formal** para 3SF o Lean Consensus

12. **No hay spec de 3SF en `ethereum/consensus-specs`** — el trabajo procede a traves de implementaciones de clientes y testing en devnets

---

## 17. Roadmap

```
2022 ─── The Merge (Sep 15) ─────────── PoW → PoS
2023 ─── Shanghai/Capella (Apr 12) ──── Withdrawals habilitados
2024 ─── Dencun (Mar 13) ───────────── Proto-danksharding (EIP-4844)
     └── Beam Chain propuesto (Nov) ─── Redeseno CL en Devcon Bangkok
2025 ─── Pectra ────────────────────── MaxEB (2048 ETH), account abstraction
     └── Lean Ethereum (Jul 31) ────── Vision completa publicada
     └── Fase de especificacion ────── Definicion tecnica formal
     └── pq-devnet-0 (Sep) ────────── Primer devnet multi-cliente
2026 ─── Desarrollo + PeerDAS ──────── Implementacion en clientes
     └── pq-devnet-1..4 ──────────── Devnets mensuales, 10K validadores
     └── Preparacion post-cuantica ── Priorizacion de tareas PQ
2027 ─── Testing ───────────────────── Devnets y testnets para Lean
2028+─── Deployments graduales ─────── Lean Consensus, Data, Execution
2029+─── Vision completa ──────────── Protocolo Lean operacional
2035 ─── Madurez ───────────────────── Lean Ethereum en forma final
```

### EIPs preparatorios ya implementados

| EIP | Upgrade | Relevancia para Lean |
|---|---|---|
| EIP-4844 (Proto-Danksharding) | Dencun 2024 | Introduce blobs y KZG, que Lean Data reemplazara con hash-based DAS |
| EIP-4788 (Beacon root en EVM) | Dencun 2024 | Acceso trustless al estado de consenso desde la capa de ejecucion |
| EIP-6780 (SELFDESTRUCT reducido) | Dencun 2024 | Simplificacion del EVM, alineado con Lean Craft |
| EIP-7251 (MaxEB a 2048 ETH) | Pectra 2025 | Consolidacion de validadores, prerrequisito para 3SF con conjuntos masivos |
| EIP-7549 (Committee index fuera de attestation) | Pectra 2025 | Mejora eficiencia de agregacion |
| EIP-6110 (Depositos on-chain) | Pectra 2025 | Simplificacion CL |
| EIP-7002 (Exits desde EL) | Pectra 2025 | Flexibilidad de staking, paso hacia 1 ETH minimo |
| EIP-7702 (Account abstraction parcial) | Pectra 2025 | Migracion gradual a firmas post-cuanticas en transacciones |

---

## 18. Personas clave

| Persona | Rol |
|---|---|
| **Justin Drake** | Ethereum Foundation researcher, arquitecto y promotor de Lean Ethereum |
| **Vitalik Buterin** | Co-fundador de Ethereum, alineado en filosofia de simplificacion, propuso RISC-V y refinamientos a 3SF |
| **Francesco D'Amato** | Investigador, autor principal del protocolo 3SF y SSF |
| **Luca Zanolini** | Investigador, co-autor de SSF y 3SF |
| **Roberto Saltini** | Investigador, co-autor del paper de 3SF |
| **Thanh Hai Tran** | Investigador, co-autor del paper de 3SF |
| **tcoratger** | Autor del plan de Lean Consensus 2026 |

---

## 19. Referencias

### Papers academicos

1. D'Amato, F., Saltini, R., Tran, T.H., & Zanolini, L. (2024). *3-Slot-Finality Protocol for Ethereum*. [arXiv:2411.00558](https://arxiv.org/abs/2411.00558)
2. D'Amato, F. & Zanolini, L. (2023). *A Simple Single Slot Finality Protocol*. [arXiv:2302.12745](https://arxiv.org/abs/2302.12745). ESORICS-CBT 2023.
3. Konnov, I., Kukovec, J., Pani, T., Tran, T.H., & Saltini, R. (2025). *Exploring Automatic Model-Checking of the Ethereum specification*. [arXiv:2501.07958](https://arxiv.org/abs/2501.07958)
4. Buterin, V. et al. (2020). *Combining GHOST and Casper*. [arXiv:2003.03052](https://arxiv.org/abs/2003.03052)
5. Buterin, V. & Griffith, V. (2017). *Casper the Friendly Finality Gadget*. [arXiv:1710.09437](https://arxiv.org/abs/1710.09437)
6. Sompolinsky, Y. & Zohar, A. (2013). *Accelerating Bitcoin's Transaction Processing: Fast Money Grows on Trees, Not Chains*.
7. Neu, J., Tas, E.N. & Tse, D. (2021). *Ebb-and-Flow Protocols: A Resolution of the Availability-Finality Dilemma*. IEEE S&P.
8. Schwarz-Schilling, C. et al. (2022). *Three Attacks on Proof-of-Stake Ethereum*. Financial Cryptography.
9. Saraswat et al. (2026). *SoK: Speedy Secure Finality*. [arXiv:2512.20715](https://arxiv.org/abs/2512.20715)
10. *LeanSig for Post-Quantum Ethereum*. [ePrint 2025/1332](https://eprint.iacr.org/2025/1332)

### Especificaciones y documentos tecnicos

11. [Chained isolated 3SF protocol — notes.ethereum.org/@fradamt/chained-3sf](https://notes.ethereum.org/@fradamt/chained-3sf)
12. [Integrating 3SF with ePBS, FOCIL, and PeerDAS — ethresear.ch/t/22909](https://ethresear.ch/t/integrating-3sf-with-epbs-focil-and-peerdas/22909)
13. [3-Slot-Finality: SSF is not about "Single" Slot — ethresear.ch/t/20927](https://ethresear.ch/t/3-slot-finality-ssf-is-not-about-single-slot/20927)
14. [View-merge as a replacement for proposer boost — ethresear.ch/t/13739](https://ethresear.ch/t/view-merge-as-a-replacement-for-proposer-boost/13739)
15. [Lean Consensus: 2026 Plan — hackmd.io/@tcoratger](https://hackmd.io/@tcoratger/ryS1ElrWbx)

### Blog posts y fuentes primarias

16. [lean Ethereum — Justin Drake, Ethereum Foundation Blog (Jul 31, 2025)](https://blog.ethereum.org/2025/07/31/lean-ethereum)
17. [Simplifying the L1 — Vitalik Buterin (May 3, 2025)](https://vitalik.eth.limo/general/2025/05/03/simplel1.html)
18. [leanroadmap.org](https://leanroadmap.org/)
19. [Lean Ethereum roadmap — CryptoSlate](https://cryptoslate.com/justin-drake-reveals-10-year-lean-ethereum-roadmap-to-achieve-10k-tps-on-mainnet/)
20. [EF makes post-quantum security a top priority — CoinDesk (Jan 2026)](https://www.coindesk.com/tech/2026/01/24/ethereum-foundation-makes-post-quantum-security-a-top-priority-as-new-team-forms)

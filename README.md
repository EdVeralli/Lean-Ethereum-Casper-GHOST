# Lean Ethereum: Paper sobre Casper FFG, LMD-GHOST y Gasper

Paper de investigacion sobre **Lean Ethereum**, la vision de Justin Drake (Ethereum Foundation, julio 2025) para la proxima decada de Ethereum.

## Documentos

### Paper Completo (18 secciones, ~1200 lineas)

| Formato | Archivo |
|---|---|
| Markdown | [`LEAN_ETHEREUM_CASPER_GHOST_Paper.md`](LEAN_ETHEREUM_CASPER_GHOST_Paper.md) |
| PDF | [`LEAN_ETHEREUM_CASPER_GHOST_Paper.pdf`](LEAN_ETHEREUM_CASPER_GHOST_Paper.pdf) |

Analisis exhaustivo con pseudocodigo de algoritmos, demostraciones formales, diagramas de arquitectura y 20 referencias academicas.

### Resumen Ejecutivo (9 secciones, ~220 lineas)

| Formato | Archivo |
|---|---|
| Markdown | [`LEAN_ETHEREUM_Resumen.md`](LEAN_ETHEREUM_Resumen.md) |
| PDF | [`LEAN_ETHEREUM_Resumen.pdf`](LEAN_ETHEREUM_Resumen.pdf) |

Version condensada con los puntos fundamentales: definiciones clave, tablas comparativas y sintesis.

### Ejemplos Practicos

#### Gasper: Consenso Actual de Ethereum

| Formato | Archivo |
|---|---|
| Markdown | [`gasper-ethereum-example.md`](gasper-ethereum-example.md) |
| PDF | [`gasper-ethereum-example.pdf`](gasper-ethereum-example.pdf) |

Ejemplo paso a paso del sistema actual de consenso (Casper FFG + LMD-GHOST) con 4 validadores, mostrando justificacion, finalizacion, resolución de forks y detección de ataques.

#### LEAN Consensus: Protocolo 3-Slot Finality

| Formato | Archivo |
|---|---|
| Markdown | [`lean-consensus-example.md`](lean-consensus-example.md) |
| PDF | [`lean-consensus-example.pdf`](lean-consensus-example.pdf) |

Ejemplo detallado del nuevo protocolo 3SF con escenarios de:
- Operacion normal (happy path)
- Resolucion de forks temporales
- Deteccion de ataques bizantinos y slashing
- Analisis de ataque del 51% y costo economico
- Comparacion: **64x mas rapido** (12.8 min → 12 seg)

## Temas cubiertos

### Parte I — Los Cimientos (Protocolo Actual)
- **GHOST y LMD-GHOST** — Fork choice rule, algoritmo formal
- **Casper FFG** — Finality gadget, slashing conditions, accountable safety
- **Gasper** — Integracion de Casper + GHOST, attestaciones, validadores, slots, epocas, comites

### Parte II — Lean Ethereum (La Transformacion)
- **Lean Consensus** (Beacon Chain 2.0) — 3-Slot Finality (~12s), min staking 1 ETH, ePBS, FOCIL, VDFs
- **Lean Data** (Blobs 2.0) — DAS post-quantum, hash-based commitments, granularidad flexible
- **Lean Execution** (EVM 2.0) — RISC-V, zkVMs en tiempo real, compatibilidad EVM
- **Lean Cryptography** — Hash-based signatures/commitments reemplazando BLS y KZG
- **Fort Mode** (defensa post-cuantica) y **Beast Mode** (1 gigagas/s L1, 1 teragas/s L2)
- **Lean Craft** — Filosofia de diseno: minimalismo, modularidad, verificacion formal
- Ataques conocidos a Gasper y como Lean los resuelve
- Roadmap 2022-2035

## Fuente primaria

- [lean Ethereum — Justin Drake, Ethereum Foundation Blog (Jul 31, 2025)](https://blog.ethereum.org/2025/07/31/lean-ethereum)
- [leanroadmap.org](https://leanroadmap.org/)
- Contacto del proyecto: lean@ethereum.org

## Referencias academicas clave

- Buterin et al. (2020) — *Combining GHOST and Casper* (arXiv:2003.03052)
- Buterin & Griffith (2017) — *Casper the Friendly Finality Gadget* (arXiv:1710.09437)
- Sompolinsky & Zohar (2013) — *GHOST Protocol*
- D'Amato & Zanolini (2023) — *A Simple Single Slot Finality Protocol*
- Neu, Tas & Tse (2021) — *Ebb-and-Flow Protocols* (IEEE S&P)
- Schwarz-Schilling et al. (2022) — *Three Attacks on Proof-of-Stake Ethereum*

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

### 🧪 Simulador Interactivo: 3SF-mini

| Directorio | Descripción |
|---|---|
| [`3sf-mini/`](3sf-mini/) | **Implementación ejecutable del protocolo 3-Slot Finality** |

Simulador completo en Python (~200 líneas) con:
- ✅ **LMD GHOST fork choice** - Implementación funcional del algoritmo
- ✅ **Backoff technique** - Justificación progresiva bajo alta latencia
- ✅ **Safe target** - Garantía de seguridad con supermayoría 2/3
- ✅ **P2P Network** - Simulador de red con latencia configurable
- ✅ **10 validadores** - Red de prueba realista

**Inicio rápido:**
```bash
cd 3sf-mini
python3 simulate.py  # Ejecuta simulación de 85 slots en ~10 segundos
```

**Documentación completa:**
- 📘 [README.md](3sf-mini/README.md) - Guía de instalación y uso
- 🚀 [QUICKSTART.md](3sf-mini/QUICKSTART.md) - Tutorial de 30 segundos
- 📊 [ANALISIS_SIMULACION.md](3sf-mini/ANALISIS_SIMULACION.md) - Resultados y métricas
- 💻 [EXAMPLES.md](3sf-mini/EXAMPLES.md) - 10+ ejemplos de código avanzado
- 📚 [INDEX.md](3sf-mini/INDEX.md) - Índice completo de recursos

**Repositorio oficial:** [ethereum/research/3sf-mini](https://github.com/ethereum/research/tree/master/3sf-mini)

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

## Implementaciones y codigo relacionado

### Spec de referencia

| Repositorio | Lenguaje | Descripcion |
|---|---|---|
| [ethereum/research/3sf-mini](https://github.com/ethereum/research/tree/master/3sf-mini) | Python | Implementacion de referencia canonica del protocolo 3SF-mini (~200 lineas) |

### Verificacion formal

| Repositorio | Lenguaje | Que verifica |
|---|---|---|
| [freespek/ssf-mc](https://github.com/freespek/ssf-mc) | TLA+ / SMT / Alloy | Model checking de 3SF con paper publicado ([arXiv:2501.07958](https://arxiv.org/abs/2501.07958)) |
| [runtimeverification/casper-proofs](https://github.com/runtimeverification/casper-proofs) | Coq | Accountable Safety y Plausible Liveness de Casper FFG |
| [runtimeverification/beacon-chain-verification](https://github.com/runtimeverification/beacon-chain-verification) | Coq | Seguridad completa de Gasper (Safety + Liveness + Slashable Bound) |
| [Koukyosyumei/PoL](https://github.com/Koukyosyumei/PoL) | Lean 4 | Verificacion de consenso simplificado (educativo/research) |

### Clientes de Lean Consensus (nueva generacion)

| Repositorio | Lenguaje | Equipo | Estado |
|---|---|---|---|
| [lambdaclass/ethlambda](https://github.com/lambdaclass/ethlambda) | Rust | LambdaClass | Activo, en pq-devnet-2 |
| [ReamLabs/ream](https://github.com/ReamLabs/ream) | Rust | Ream Labs | Activo |
| [blockblaz/zeam](https://github.com/blockblaz/zeam) | Zig | Blockblaz | WIP, financiado por la EF |
| [qdrvm](https://github.com/qdrvm) (Qlean) | C++ | Quadrivium | Activo en devnets |
| [Pier-Two](https://github.com/Pier-Two) (Lantern) | C | Pier Two | Activo |
| [grandinetech/grandine](https://github.com/grandinetech/grandine) | Rust | Grandine Tech | Produccion + colaborando con Lean |
| [sigp/lighthouse](https://github.com/sigp/lighthouse) | Rust | Sigma Prime | Fork interno para Lean |

### Infraestructura de devnets

| Repositorio | Descripcion |
|---|---|
| [blockblaz/lean-quickstart](https://github.com/blockblaz/lean-quickstart) | Herramienta para levantar redes locales multi-cliente |
| [ReamLabs/lean-spec-tests](https://github.com/ReamLabs/lean-spec-tests) | Tests comunes para clientes de Lean Consensus |
| [ReamLabs/leanroadmap](https://github.com/ReamLabs/leanroadmap) | Tracking del progreso de investigacion de Lean Consensus |

### Papers de 3SF

- D'Amato & Zanolini (2023) — *A Simple Single Slot Finality Protocol* ([arXiv:2302.12745](https://arxiv.org/abs/2302.12745))
- D'Amato, Saltini, Tran & Zanolini (2024) — *3SF: 3-Slot Finality* ([arXiv:2411.00558](https://arxiv.org/abs/2411.00558))

> **Nota:** A la fecha (febrero 2026) no existe una formalizacion en Lean 4 de Casper FFG, LMD-GHOST ni Gasper. Las pruebas formales existentes usan Coq y TLA+.

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

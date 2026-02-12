# Lean Ethereum: Paper sobre Casper FFG, LMD-GHOST y Gasper

Paper de investigacion sobre **Lean Ethereum**, la vision de Justin Drake (Ethereum Foundation, julio 2025) para la proxima decada de Ethereum.

## Contenido

- **`LEAN_ETHEREUM_CASPER_GHOST_Paper.md`** — Paper completo en Markdown
- **`LEAN_ETHEREUM_CASPER_GHOST_Paper.pdf`** — Paper completo en PDF

## Temas cubiertos

### Parte I — Los Cimientos (Protocolo Actual)
- GHOST y LMD-GHOST (fork choice rule)
- Casper FFG (finality gadget, slashing conditions, accountable safety)
- Gasper (integracion de Casper + GHOST)
- Validadores, slots, epocas, comites

### Parte II — Lean Ethereum (La Transformacion)
- **Lean Consensus** (Beacon Chain 2.0): 3-Slot Finality (~12s), min staking 1 ETH, ePBS, FOCIL, VDFs
- **Lean Data** (Blobs 2.0): DAS post-quantum, hash-based commitments
- **Lean Execution** (EVM 2.0): RISC-V, zkVMs en tiempo real
- **Lean Cryptography**: Hash-based signatures/commitments reemplazando BLS y KZG
- Fort Mode (defensa post-cuantica) y Beast Mode (1 gigagas/s L1, 1 teragas/s L2)
- Ataques conocidos a Gasper y como Lean los resuelve
- Roadmap 2022-2035

## Fuente primaria

- [lean Ethereum — Justin Drake, Ethereum Foundation Blog (Jul 31, 2025)](https://blog.ethereum.org/2025/07/31/lean-ethereum)
- [leanroadmap.org](https://leanroadmap.org/)

## Referencias academicas clave

- Buterin et al. (2020) — *Combining GHOST and Casper* (arXiv:2003.03052)
- Buterin & Griffith (2017) — *Casper the Friendly Finality Gadget* (arXiv:1710.09437)
- Sompolinsky & Zohar (2013) — *GHOST Protocol*
- D'Amato & Zanolini (2023) — *A Simple Single Slot Finality Protocol*

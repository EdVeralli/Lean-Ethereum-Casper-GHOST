# 📚 Índice de Documentación - 3SF-mini

Guía completa para navegar todos los recursos del simulador 3SF-mini.

---

## 🚀 Comenzar Rápido

1. **[QUICKSTART.md](QUICKSTART.md)** - Ejecuta tu primera simulación en 30 segundos
   ```bash
   cd 3sf-mini && python3 simulate.py
   ```

---

## 📖 Documentación Principal

### Para Usuarios
- **[README.md](README.md)** - Guía completa de instalación, uso y configuración
  - Requisitos del sistema
  - Instalación paso a paso
  - Estructura del proyecto
  - Configuración avanzada
  - Troubleshooting

### Para Desarrolladores
- **[EXAMPLES.md](EXAMPLES.md)** - 10+ ejemplos de código y extensiones
  - Modificar parámetros
  - Agregar validadores bizantinos
  - Simular particiones de red
  - Análisis de datos
  - Visualización

### Análisis de Resultados
- **[ANALISIS_SIMULACION.md](ANALISIS_SIMULACION.md)** - Análisis detallado de una ejecución
  - Impacto de la latencia
  - Métricas de convergencia
  - Comparación con Gasper
  - Experimentos sugeridos

---

## 📂 Archivos de Código

### Core del Protocolo
```
consensus.py (200 líneas)
├── Config, State, Vote, Block    # Estructuras de datos
├── is_justifiable_slot()          # Backoff technique
├── process_block()                # Procesamiento de bloques
└── get_fork_choice_head()         # LMD GHOST

p2p.py (350 líneas)
├── Staker                         # Validador
│   ├── propose_block()           # t=0: Proponer
│   ├── vote()                    # t=3s: Votar
│   ├── compute_safe_target()     # t=6s: Safe target
│   └── accept_new_votes()        # t=9s: View merge
└── P2PNetwork                     # Simulador de red

simulate.py (80 líneas)
└── Script principal de simulación
```

### Scripts de Utilidad
- **run_experiments.sh** - Ejecutar múltiples experimentos automáticamente
- **requirements.txt** - Dependencias opcionales (matplotlib, networkx)
- **.gitignore** - Ignorar archivos temporales

---

## 🎯 Flujos de Trabajo Comunes

### 1️⃣ Primera Vez Usando 3SF-mini
```
QUICKSTART.md → Ejecutar simulate.py → ANALISIS_SIMULACION.md
```

### 2️⃣ Entender el Código en Profundidad
```
README.md (Estructura) → consensus.py → p2p.py → simulate.py
```

### 3️⃣ Modificar y Experimentar
```
EXAMPLES.md → Elegir ejemplo → Modificar simulate.py → Ejecutar
```

### 4️⃣ Benchmarks y Comparaciones
```
run_experiments.sh → Analizar logs → Comparar resultados
```

### 5️⃣ Agregar Features Nuevos
```
EXAMPLES.md → consensus.py/p2p.py → Crear clase nueva → Integrar en simulate.py
```

---

## 📊 Matriz de Recursos por Objetivo

| Objetivo | Recursos | Tiempo |
|----------|----------|--------|
| **Ejecutar primera simulación** | QUICKSTART.md | 2 min |
| **Entender el protocolo** | README.md + consensus.py | 30 min |
| **Modificar parámetros** | EXAMPLES.md (Ejemplo 4-5) | 10 min |
| **Agregar validadores bizantinos** | EXAMPLES.md (Ejemplo 6-7) | 20 min |
| **Simular particiones** | EXAMPLES.md (Ejemplo 8) | 30 min |
| **Análisis de datos** | EXAMPLES.md (Ejemplo 9-10) | 45 min |
| **Benchmarks automáticos** | run_experiments.sh | 5 min |

---

## 🔍 Buscar Información Específica

### "¿Cómo instalo las dependencias?"
→ **README.md** - Sección "Instalación"

### "¿Cómo cambio el número de validadores?"
→ **QUICKSTART.md** - Sección "Modificaciones Comunes"
→ **EXAMPLES.md** - Ejemplo 4

### "¿Cómo funciona LMD GHOST?"
→ **README.md** - Sección "Estructura del Proyecto"
→ **consensus.py** - Función `get_fork_choice_head()` (línea ~120)

### "¿Cómo interpreto los resultados?"
→ **ANALISIS_SIMULACION.md** - Toda la sección
→ **README.md** - Sección "Entendiendo la Salida"

### "¿Cómo agrego un validador malicioso?"
→ **EXAMPLES.md** - Ejemplos 6-7

### "¿Cómo visualizo el árbol de bloques?"
→ **EXAMPLES.md** - Ejemplo 10
→ **requirements.txt** + `pip install matplotlib networkx`

### "¿Qué significa 'Finalized slot 82'?"
→ **README.md** - Sección "Entendiendo la Salida"
→ **ANALISIS_SIMULACION.md** - Sección "Métricas"

### "¿Cómo ejecuto múltiples experimentos?"
→ **run_experiments.sh**
→ **EXAMPLES.md** - Ejemplo 11

---

## 🎓 Ruta de Aprendizaje Sugerida

### Nivel 1: Principiante (1-2 horas)
1. Leer **QUICKSTART.md**
2. Ejecutar `python3 simulate.py`
3. Leer **README.md** secciones: Descripción, Uso Rápido, Entendiendo la Salida
4. Revisar **ANALISIS_SIMULACION.md**

### Nivel 2: Intermedio (3-5 horas)
1. Leer **README.md** completo
2. Estudiar `consensus.py` línea por línea
3. Estudiar `p2p.py` línea por línea
4. Modificar parámetros básicos (validadores, latencia)
5. Ejecutar **run_experiments.sh**

### Nivel 3: Avanzado (5-10 horas)
1. Leer **EXAMPLES.md** completo
2. Implementar validador bizantino (Ejemplo 6)
3. Implementar partición de red (Ejemplo 8)
4. Crear script de análisis personalizado (Ejemplo 9)
5. Agregar visualización (Ejemplo 10)

### Nivel 4: Experto (10+ horas)
1. Leer papers académicos (ver README.md - Referencias)
2. Implementar extensiones propias
3. Comparar con otros protocolos de consenso
4. Contribuir al repositorio ethereum/research

---

## 📞 Soporte y Recursos Externos

### Documentación Oficial
- **Repositorio:** [ethereum/research/3sf-mini](https://github.com/ethereum/research/tree/master/3sf-mini)
- **Paper 3SF:** [arXiv:2411.00558](https://arxiv.org/abs/2411.00558)
- **Blog Lean Ethereum:** [blog.ethereum.org](https://blog.ethereum.org/2025/07/31/lean-ethereum)

### Comunidad
- **Ethresear.ch:** [ethresear.ch](https://ethresear.ch/)
- **Ethereum Research GitHub:** [github.com/ethereum/research](https://github.com/ethereum/research)
- **Email:** lean@ethereum.org

---

## 🗺️ Mapa Visual

```
3sf-mini/
│
├─ 📘 DOCUMENTACIÓN
│  ├─ INDEX.md (este archivo)       ← Navegación
│  ├─ README.md                     ← Guía completa
│  ├─ QUICKSTART.md                 ← Start here!
│  ├─ EXAMPLES.md                   ← Código avanzado
│  └─ ANALISIS_SIMULACION.md        ← Resultados
│
├─ 💻 CÓDIGO
│  ├─ consensus.py                  ← Protocolo core
│  ├─ p2p.py                        ← Red + Validadores
│  └─ simulate.py                   ← Script principal
│
└─ 🛠️ HERRAMIENTAS
   ├─ run_experiments.sh            ← Benchmarks
   ├─ requirements.txt              ← Dependencias
   └─ .gitignore                    ← Git config
```

---

## ✅ Checklist de Inicio

- [ ] Leer **QUICKSTART.md**
- [ ] Ejecutar `python3 simulate.py`
- [ ] Ver resultado completo (esperar ~10 segundos)
- [ ] Leer **README.md** secciones principales
- [ ] Revisar **ANALISIS_SIMULACION.md**
- [ ] Modificar un parámetro en `simulate.py`
- [ ] Re-ejecutar y comparar resultados
- [ ] Explorar **EXAMPLES.md** para ideas avanzadas

---

**¡Listo para comenzar!** 🚀

Si tienes dudas, empieza por **QUICKSTART.md** o abre un issue en el repositorio.

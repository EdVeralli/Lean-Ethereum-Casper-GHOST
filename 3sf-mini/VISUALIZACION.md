# 🎨 Visualización del Árbol de Bloques - 3SF

Guía completa para generar y entender las visualizaciones del simulador 3SF-mini.

---

## 🚀 Ejecución Rápida

```bash
# Instalar dependencias
pip install matplotlib networkx

# Ejecutar simulación con visualización
python3 simulate_save_viz.py

# Ver las imágenes generadas
open visualizations/
```

---

## 📊 ¿Qué Visualiza?

El simulador genera **imágenes del árbol de bloques** mostrando:

### 🔵 Código de Colores

| Color | Significado | Descripción |
|-------|-------------|-------------|
| 🟢 **Verde** | **Head** | Bloque elegido por LMD GHOST como cabeza de la cadena |
| 🔵 **Azul** | **Justified** | Bloque con 2/3 de votos de validadores (checkpoint) |
| 🟣 **Púrpura** | **Finalized** | Bloque irreversible (finalizado) |
| ⚪ **Gris** | Normal | Bloque válido pero sin status especial |
| 🟠 **Naranja** | **Votantes** | Validadores emitiendo votos |

### 📍 Elementos Visuales

- **Círculos grandes**: Bloques de la blockchain
  - Etiqueta: `[hash]` + `S[slot]`
  - Ejemplo: `bd7dc661 S1` = bloque con hash bd7dc661 en slot 1

- **Círculos pequeños naranjas**: Validadores votando
  - Etiqueta: `V0`, `V1`, ..., `V9` (validator ID)

- **Flechas sólidas**: Conexiones parent → child entre bloques

- **Flechas naranjas discontinuas** (---): Voto por **head** (LMD GHOST)

- **Flechas grises punteadas** (···): Voto por **target** (justificación)

### 📦 Información de Estado

Cada visualización incluye un cuadro informativo con:
```
Total Blocks: 27        # Número de bloques en la cadena
Total Votes: 250        # Votos emitidos por validadores
Finalized Slot: 21      # Último slot finalizado
Justified Slot: 24      # Último slot justificado
```

---

## 📁 Archivos Generados

La simulación crea el directorio `visualizations/` con:

```
visualizations/
├── block_tree_slot_002.png   # Slot 2 (inicio)
├── block_tree_slot_007.png   # Slot 7
├── block_tree_slot_012.png   # Slot 12
├── ...                        # Cada 5 slots
├── block_tree_slot_082.png   # Slot 82
└── block_tree_final_slot_85.png  # Estado final
```

**Frecuencia**: Una imagen cada **60 time units** (~5 slots) + imagen final

**Total**: ~18 imágenes por simulación estándar (1000 time units)

---

## 🔍 Interpretando las Visualizaciones

### Ejemplo 1: Slot Inicial (Slot 7)

```
Estado temprano:
- Pocos bloques
- Genesis en la parte inferior
- Votantes concentrados en bloques recientes
- Justified/Finalized pueden estar varios slots atrás
```

### Ejemplo 2: Medio de Simulación (Slot 27)

**Lo que verás:**
- ✅ Múltiples ramas (forks temporales)
- ✅ Bloque **azul** (justified) en una rama
- ✅ Bloque **púrpura** (finalized) más atrás
- ✅ Bloque **verde** (head) en la punta de la rama principal
- ✅ Votantes (naranjas) concentrados cerca del head

**Esto muestra:**
- El protocolo está funcionando correctamente
- Los validadores convergen hacia una rama principal
- La finalidad progresa gradualmente

### Ejemplo 3: Alta Latencia vs Baja Latencia

#### **Alta Latencia (antes del slot 55):**
```
- Árbol más "ancho" (muchas ramas)
- Votantes dispersos
- Mayor distancia entre finalized y head
- Convergencia lenta
```

#### **Baja Latencia (después del slot 55):**
```
- Árbol más "lineal" (pocas ramas)
- Votantes concentrados
- Menor distancia entre finalized y head
- Convergencia rápida
```

---

## 📈 Casos de Uso

### 1. Estudiar Convergencia

Compara múltiples slots secuenciales:
```bash
# Ver slots 27, 32, 37, 42
open visualizations/block_tree_slot_027.png
open visualizations/block_tree_slot_032.png
open visualizations/block_tree_slot_037.png
open visualizations/block_tree_slot_042.png
```

**Observa:**
- ¿Se reduce el número de ramas?
- ¿Los validadores votan por la misma rama?
- ¿La finalidad avanza?

### 2. Detectar Forks

```bash
# Buscar slots con muchas ramas
ls -lh visualizations/*.png | sort -k5 -rn
# Archivos más grandes = árboles más complejos = más forks
```

### 3. Medir Tiempo de Finalidad

```bash
# Ver cuántos slots pasan entre justified y finalized
python3 -c "
import re
files = sorted(glob.glob('visualizations/*.png'))
for f in files:
    # Extraer info del filename y analizar
"
```

### 4. Comparar Experimentos

Ejecuta múltiples simulaciones con diferentes parámetros:
```bash
# Experimento 1: 10 validadores
python3 simulate_save_viz.py
mv visualizations viz_10_validators

# Experimento 2: 50 validadores
# (modificar NUM_STAKERS = 50)
python3 simulate_save_viz.py
mv visualizations viz_50_validators

# Comparar visualmente
open viz_10_validators/block_tree_final*.png
open viz_50_validators/block_tree_final*.png
```

---

## 🎥 Crear Animación (GIF)

Convierte las imágenes en un GIF animado:

### Opción 1: ImageMagick
```bash
brew install imagemagick  # macOS
# o apt-get install imagemagick  # Linux

cd visualizations
convert -delay 50 -loop 0 block_tree_slot_*.png animation.gif
```

### Opción 2: ffmpeg
```bash
brew install ffmpeg  # macOS

cd visualizations
ffmpeg -framerate 2 -pattern_type glob -i 'block_tree_slot_*.png' \
       -vf "scale=1280:-1" output.mp4
```

### Opción 3: Python
```python
from PIL import Image
import glob

images = []
for filename in sorted(glob.glob('visualizations/block_tree_slot_*.png')):
    images.append(Image.open(filename))

images[0].save('animation.gif',
               save_all=True,
               append_images=images[1:],
               duration=500,  # ms por frame
               loop=0)
```

---

## ⚙️ Personalización

### Modificar Frecuencia de Visualización

Edita `simulate_save_viz.py` línea 176:
```python
# Cada 5 slots (default)
if time % 60 == 9:
    plot_view(...)

# Cambiar a cada slot
if time % SLOT_DURATION == 0:
    plot_view(...)

# Cambiar a cada 10 slots
if time % 120 == 9:
    plot_view(...)
```

### Cambiar Tamaño de Imagen

Línea 22:
```python
# Más grande (mejor calidad)
fig, ax = plt.subplots(figsize=(20, 16))

# Más pequeño (menor tamaño de archivo)
fig, ax = plt.subplots(figsize=(12, 8))
```

### Cambiar DPI (Resolución)

Línea 122:
```python
# Alta resolución
plt.savefig(filename, dpi=300, bbox_inches='tight')

# Baja resolución (archivos más pequeños)
plt.savefig(filename, dpi=100, bbox_inches='tight')
```

### Modificar Colores

Líneas 58-65:
```python
if node == justified_hash[:8]:
    node_colors.append("#FF6B6B")  # Rojo personalizado
elif node == finalized_hash[:8]:
    node_colors.append("#4ECDC4")  # Turquesa personalizado
# ... etc
```

---

## 🐛 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'matplotlib'`

**Solución:**
```bash
pip3 install matplotlib networkx
```

### Error: `backend is non-GUI backend 'agg'`

**Causa:** Estás intentando usar `simulate_with_viz.py` sin display gráfico

**Solución:** Usa `simulate_save_viz.py` en su lugar (guarda archivos en lugar de mostrar ventanas)

### Visualizaciones muy grandes (>500 KB cada una)

**Solución:** Reduce el DPI o el tamaño:
```python
fig, ax = plt.subplots(figsize=(12, 8))  # Más pequeño
plt.savefig(filename, dpi=100)  # Menor resolución
```

### No se generan todas las imágenes

**Causa:** Simulación muy corta o frecuencia de visualización muy espaciada

**Solución:** Aumenta `range(1000)` a `range(2000)` o visualiza más frecuentemente

---

## 📚 Recursos Adicionales

### Entender los Algoritmos

- **LMD GHOST**: `consensus.py` línea 120 (`get_fork_choice_head()`)
- **Justification**: `consensus.py` línea 72 (`process_block()`)
- **Finalization**: `consensus.py` línea 87 (dentro de `process_block()`)

### Papers de Referencia

- **3-Slot Finality**: [arXiv:2411.00558](https://arxiv.org/abs/2411.00558)
- **Gasper**: [arXiv:2003.03052](https://arxiv.org/abs/2003.03052)
- **LMD GHOST**: Sección 3 del paper de Gasper

---

## 💡 Tips Avanzados

### 1. Visualizar Solo un Validador Específico

Modifica línea 173:
```python
# En lugar de stakers[0], elige otro validador
plot_view(stakers[5], filename, title)  # Visualizar validador 5
```

### 2. Comparar Vistas de Múltiples Validadores

```python
# Guardar vista de cada validador
for i in range(NUM_STAKERS):
    filename = f"{viz_dir}/validator_{i}_slot_{current_slot}.png"
    plot_view(stakers[i], filename, f"Validator {i} - Slot {current_slot}")
```

### 3. Highlight de Bloques Específicos

Agrega lógica personalizada en `plot_view()`:
```python
# Highlight bloques con >5 votos
for block_hash in high_vote_blocks:
    if block_hash[:8] in pos:
        # Dibujar con borde especial
        nx.draw_networkx_nodes(G, pos, nodelist=[block_hash[:8]],
                              node_color='yellow',
                              edgecolors='red', linewidths=3)
```

---

## 📊 Análisis Estadístico de Visualizaciones

```python
import re
import glob
from PIL import Image

# Analizar complejidad del árbol por tamaño de archivo
files = glob.glob('visualizations/block_tree_slot_*.png')
for f in sorted(files):
    slot = re.search(r'slot_(\d+)', f).group(1)
    size = os.path.getsize(f) // 1024  # KB
    print(f"Slot {slot}: {size} KB")

# Slots con archivos grandes = más forks/complejidad
```

---

## ✅ Checklist de Visualización

- [ ] Instalar matplotlib y networkx
- [ ] Ejecutar `python3 simulate_save_viz.py`
- [ ] Verificar directorio `visualizations/` creado
- [ ] Abrir imagen final para ver resultado
- [ ] Comparar 2-3 slots intermedios
- [ ] Identificar bloques justified/finalized/head
- [ ] Observar convergencia de validadores
- [ ] (Opcional) Crear GIF animado
- [ ] (Opcional) Comparar con diferentes parámetros

---

**¡Listo para visualizar!** 🎨

Si encuentras bugs o tienes sugerencias, abre un issue en el repositorio.

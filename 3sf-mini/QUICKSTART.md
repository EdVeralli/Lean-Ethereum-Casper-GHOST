# 🚀 Quick Start - 3SF-mini

## En 30 segundos

```bash
# 1. Navega al directorio
cd 3sf-mini

# 2. Ejecuta la simulación
python3 simulate.py

# 3. Listo! Verás la salida en tiempo real
```

---

## Comandos Útiles

### Ver solo el resumen final
```bash
python3 simulate.py | tail -10
```

### Guardar logs
```bash
python3 simulate.py > mi_simulacion.log
```

### Ver solo los momentos clave (cada slot)
```bash
python3 simulate.py | grep "=== Time"
```

### Ver convergencia en un slot específico (ej: slot 60)
```bash
python3 simulate.py | grep -A 10 "Slot 60" | head -15
```

---

## Modificaciones Comunes

### Cambiar número de validadores

Abre `simulate.py` y modifica línea 8:
```python
NUM_STAKERS = 50  # Era 10, ahora 50
```

### Cambiar duración de simulación

Abre `simulate.py` y modifica línea 45:
```python
for time in range(3000):  # Era 1000, ahora 3000 (250 slots)
```

### Cambiar latencia de red

Abre `simulate.py` y modifica líneas 31-35:
```python
def latency_func(t):
    return 1  # Siempre latencia mínima
```

---

## Problemas Comunes

### ❌ `ModuleNotFoundError: No module named 'consensus'`
✅ **Solución:** Ejecuta desde dentro del directorio `3sf-mini/`

### ❌ `python: command not found`
✅ **Solución:** Usa `python3` en lugar de `python`

### ❌ Simulación muy lenta
✅ **Solución:** Reduce `NUM_STAKERS` a 10 o menos

---

## Leer Más

📖 **README completo:** [README.md](README.md)
📊 **Análisis de resultados:** [ANALISIS_SIMULACION.md](ANALISIS_SIMULACION.md)

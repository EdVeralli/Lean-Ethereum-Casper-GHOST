#!/bin/bash

# Script para ejecutar múltiples experimentos con 3SF-mini
# Uso: ./run_experiments.sh

set -e

echo "🧪 Ejecutando experimentos con 3SF-mini"
echo "========================================"

# Crear directorio de resultados
mkdir -p results
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Experimento 1: Simulación básica (baseline)
echo ""
echo "📊 Experimento 1: Baseline (10 validadores, 1000 time units)"
python3 simulate.py > results/exp1_baseline_${TIMESTAMP}.log
echo "✅ Guardado en: results/exp1_baseline_${TIMESTAMP}.log"

# Experimento 2: Más validadores
echo ""
echo "📊 Experimento 2: Escalar validadores"
for n in 10 20 50; do
    echo "  - Simulando con $n validadores..."
    # Nota: Necesitas modificar NUM_STAKERS en simulate.py para cada valor
    # O usar sed para automatizar:
    sed "s/NUM_STAKERS = 10/NUM_STAKERS = $n/" simulate.py > simulate_temp.py
    python3 simulate_temp.py > results/exp2_validators_${n}_${TIMESTAMP}.log
    rm simulate_temp.py
    echo "  ✅ Guardado en: results/exp2_validators_${n}_${TIMESTAMP}.log"
done

# Experimento 3: Simulación larga
echo ""
echo "📊 Experimento 3: Simulación extendida (5000 time units)"
sed "s/range(1000)/range(5000)/" simulate.py > simulate_temp.py
python3 simulate_temp.py > results/exp3_long_${TIMESTAMP}.log
rm simulate_temp.py
echo "✅ Guardado en: results/exp3_long_${TIMESTAMP}.log"

# Resumen
echo ""
echo "========================================"
echo "🎉 Experimentos completados!"
echo ""
echo "📁 Resultados guardados en: results/"
ls -lh results/*${TIMESTAMP}.log

# Análisis rápido
echo ""
echo "📊 Resumen de Resultados:"
echo "------------------------"
for file in results/*${TIMESTAMP}.log; do
    echo ""
    echo "📄 $(basename $file):"
    grep "Estado Final" -A 4 "$file" || echo "  (no finalizado)"
done

echo ""
echo "💡 Tip: Revisa los logs completos con:"
echo "   cat results/exp1_baseline_${TIMESTAMP}.log"

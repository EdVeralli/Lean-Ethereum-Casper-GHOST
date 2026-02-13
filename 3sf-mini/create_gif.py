#!/usr/bin/env python3
"""
Crea un GIF animado mostrando la transición de alta a baja latencia
"""
from PIL import Image
import glob
import os

# Slots clave para mostrar la transición
key_slots = [42, 47, 52, 57, 62, 67, 72, 77, 82]

images = []
viz_dir = "visualizations"

print("🎬 Creando GIF animado de transición de latencia...")
print(f"   Slots: {key_slots}")

for slot in key_slots:
    filename = f"{viz_dir}/block_tree_slot_{slot:03d}.png"
    if os.path.exists(filename):
        img = Image.open(filename)
        images.append(img)
        print(f"   ✅ Agregado: slot {slot}")
    else:
        print(f"   ⚠️  No encontrado: slot {slot}")

if images:
    output_file = f"{viz_dir}/latency_transition.gif"

    # Crear GIF con duración variable:
    # - Más lento en slot 52 (antes del cambio)
    # - Muy lento en slot 57 (momento del cambio)
    # - Más lento en slot 72 (después del cambio)
    durations = []
    for slot in key_slots[:len(images)]:
        if slot == 57:  # Momento exacto del cambio
            durations.append(2000)  # 2 segundos
        elif slot in [52, 72]:  # Momentos clave antes/después
            durations.append(1500)  # 1.5 segundos
        else:
            durations.append(800)  # 0.8 segundos normal

    images[0].save(
        output_file,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,  # Loop infinito
        optimize=False
    )

    file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
    print(f"\n✅ GIF creado exitosamente!")
    print(f"   Archivo: {output_file}")
    print(f"   Frames: {len(images)}")
    print(f"   Tamaño: {file_size:.2f} MB")
    print(f"\n📊 Timeline del GIF:")
    print(f"   Slot 42-52: 🔴 Alta latencia")
    print(f"   Slot 57:    🟡 TRANSICIÓN (pausa 2s)")
    print(f"   Slot 62-82: 🟢 Baja latencia")
else:
    print("❌ No se encontraron imágenes para crear el GIF")

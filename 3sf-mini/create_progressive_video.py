#!/usr/bin/env python3
"""
Crea un video mostrando la construcción PROGRESIVA del blockchain
Cada slot muestra cómo el árbol va creciendo
"""
import imageio.v3 as iio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import glob

viz_dir = "visualizations"
output_file = f"{viz_dir}/blockchain_construction.mp4"

print("🎬 Creando video de CONSTRUCCIÓN PROGRESIVA del blockchain...")

# Obtener todos los slots disponibles
slot_files = sorted(glob.glob(f"{viz_dir}/block_tree_slot_*.png"))
print(f"   Slots disponibles: {len(slot_files)}")

# Configuración
fps = 30

def add_construction_annotation(img, slot_num, total_slots):
    """Agrega anotación mostrando progreso de construcción"""
    img_copy = img.copy()
    draw = ImageDraw.Draw(img_copy)

    # Fuente
    try:
        font_big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 70)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        font_big = ImageFont.load_default()
        font_small = font_big

    img_width, img_height = img_copy.size

    # Banner superior: Slot actual
    if slot_num <= 52:
        banner_color = 'red'
        status = "🔴 ALTA LATENCIA"
    elif slot_num == 57:
        banner_color = 'yellow'
        status = "⚡ TRANSICIÓN"
    elif slot_num <= 67:
        banner_color = 'orange'
        status = "🟡 MEJORANDO"
    else:
        banner_color = 'green'
        status = "🟢 BAJA LATENCIA"

    # Texto principal
    main_text = f"Slot {slot_num}"
    bbox = draw.textbbox((0, 0), main_text, font=font_big)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (img_width - text_width) // 2
    y = 30

    # Fondo del texto
    padding = 20
    draw.rectangle(
        [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
        fill='black',
        outline=banner_color,
        width=5
    )
    draw.text((x, y), main_text, fill=banner_color, font=font_big)

    # Estado debajo
    status_bbox = draw.textbbox((0, 0), status, font=font_small)
    status_width = status_bbox[2] - status_bbox[0]
    status_x = (img_width - status_width) // 2
    status_y = y + text_height + 10
    draw.text((status_x, status_y), status, fill=banner_color, font=font_small)

    # Barra de progreso en la parte inferior
    bar_height = 40
    bar_y = img_height - bar_height - 20
    bar_width = img_width - 100
    bar_x = 50

    # Fondo de la barra
    draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                   fill='black', outline='white', width=3)

    # Progreso
    progress = (slot_num - 2) / (total_slots - 2)  # slot 2 = inicio, slot final = 100%
    progress_width = int(bar_width * progress)
    draw.rectangle([bar_x, bar_y, bar_x + progress_width, bar_y + bar_height],
                   fill=banner_color)

    # Texto de progreso
    progress_text = f"Construcción: {progress*100:.0f}%"
    prog_bbox = draw.textbbox((0, 0), progress_text, font=font_small)
    prog_width = prog_bbox[2] - prog_bbox[0]
    prog_x = (img_width - prog_width) // 2
    prog_y = bar_y - prog_bbox[3] - 10
    draw.text((prog_x, prog_y), progress_text, fill='white', font=font_small)

    return img_copy

frames = []

# Extraer número de slot de cada archivo
slot_numbers = []
for f in slot_files:
    slot_num = int(f.split('_slot_')[1].split('.')[0])
    slot_numbers.append(slot_num)

max_slot = max(slot_numbers)

for i, (slot_file, slot_num) in enumerate(zip(slot_files, slot_numbers)):
    # Cargar imagen
    img = Image.open(slot_file)

    # Agregar anotaciones de construcción
    annotated = add_construction_annotation(img, slot_num, max_slot)

    # Convertir a numpy array
    frame = np.array(annotated)

    # Duración variable según importancia del slot
    if slot_num == 2:
        duration = 2.0  # Inicio - más tiempo
    elif slot_num == 57:
        duration = 3.0  # Transición - máximo tiempo
    elif slot_num in [52, 72]:
        duration = 2.5  # Momentos clave
    elif slot_num == max_slot:
        duration = 3.0  # Final - mucho tiempo
    else:
        duration = 1.2  # Normal - suficiente para ver cambios

    num_frames = int(duration * fps)

    # Agregar frames
    for _ in range(num_frames):
        frames.append(frame)

    print(f"   ✅ Slot {slot_num:3d}: {duration}s ({num_frames} frames)")

if frames:
    total_duration = len(frames) / fps
    print(f"\n💾 Guardando video...")
    print(f"   Total frames: {len(frames)}")
    print(f"   FPS: {fps}")
    print(f"   Duración total: {total_duration:.1f} segundos")

    # Guardar como MP4
    iio.imwrite(
        output_file,
        frames,
        fps=fps,
        codec='libx264',
        quality=9,
        pixelformat='yuv420p',
        macro_block_size=16
    )

    file_size = os.path.getsize(output_file) / (1024 * 1024)

    print(f"\n✅ Video de construcción creado exitosamente!")
    print(f"   📁 Archivo: {output_file}")
    print(f"   📊 Slots mostrados: {len(slot_files)}")
    print(f"   ⏱️  Duración: {total_duration:.1f}s (~{total_duration/60:.1f} min)")
    print(f"   💾 Tamaño: {file_size:.2f} MB")

    print(f"\n🎬 Este video muestra:")
    print(f"   ✅ La construcción progresiva del blockchain")
    print(f"   ✅ Cómo el árbol crece slot por slot")
    print(f"   ✅ Indicador visual del slot actual")
    print(f"   ✅ Barra de progreso de construcción")
    print(f"   ✅ Estado de latencia en cada momento")
    print(f"   ✅ {len(slot_files)} snapshots del blockchain en evolución")

    print(f"\n📊 Timeline:")
    cumulative = 0
    for i, (slot_num) in enumerate(slot_numbers[:5]):
        if slot_num == 2:
            dur = 2.0
        elif slot_num == 57:
            dur = 3.0
        elif slot_num in [52, 72]:
            dur = 2.5
        else:
            dur = 1.2
        print(f"   {cumulative:5.1f}s: Slot {slot_num}")
        cumulative += dur
    print(f"   ...")
    print(f"   {total_duration:5.1f}s: Slot {max_slot} (final)")

    print(f"\n🎥 Para ver:")
    print(f"   open {output_file}")
else:
    print("❌ No se encontraron imágenes")

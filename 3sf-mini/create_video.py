#!/usr/bin/env python3
"""
Crea un video MP4 mostrando la transición de alta a baja latencia
"""
import imageio.v3 as iio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# Slots clave para mostrar la transición
key_slots = [42, 47, 52, 57, 62, 67, 72, 77, 82]

viz_dir = "visualizations"
output_file = f"{viz_dir}/latency_transition.mp4"

print("🎬 Creando video MP4 de transición de latencia...")
print(f"   Slots: {key_slots}")

# Configuración de duración (en frames, asumiendo 30 fps)
fps = 30
durations_seconds = {
    42: 1.0,   # Normal
    47: 1.0,   # Normal
    52: 2.0,   # Pausa antes del cambio
    57: 3.0,   # PAUSA LARGA en el momento del cambio
    62: 1.5,   # Después del cambio
    67: 1.5,   # Convergencia
    72: 2.0,   # Pausa después del cambio
    77: 1.0,   # Normal
    82: 2.0,   # Final - pausa larga
}

frames = []

def add_annotation(img, text, position='top', color='red'):
    """Agrega anotación de texto a la imagen"""
    img_copy = img.copy()
    draw = ImageDraw.Draw(img_copy)

    # Intentar usar una fuente más grande
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        font = ImageFont.load_default()

    # Obtener tamaño del texto
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calcular posición
    img_width, img_height = img_copy.size
    x = (img_width - text_width) // 2

    if position == 'top':
        y = 50
    else:  # bottom
        y = img_height - text_height - 50

    # Dibujar fondo para el texto
    padding = 20
    draw.rectangle(
        [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
        fill='black',
        outline=color,
        width=5
    )

    # Dibujar texto
    draw.text((x, y), text, fill=color, font=font)

    return img_copy

for slot in key_slots:
    filename = f"{viz_dir}/block_tree_slot_{slot:03d}.png"

    if not os.path.exists(filename):
        print(f"   ⚠️  No encontrado: slot {slot}")
        continue

    # Cargar imagen
    img = Image.open(filename)

    # Agregar anotaciones según el slot
    if slot <= 52:
        # Alta latencia
        annotated = add_annotation(img, "🔴 ALTA LATENCIA", 'top', 'red')
    elif slot == 57:
        # Momento del cambio
        annotated = add_annotation(img, "⚡ CAMBIO DE LATENCIA (t=667)", 'top', 'yellow')
        annotated = add_annotation(annotated, "Alta → Baja", 'bottom', 'yellow')
    elif slot <= 67:
        # Transición
        annotated = add_annotation(img, "🟡 TRANSICIÓN", 'top', 'orange')
    else:
        # Baja latencia
        annotated = add_annotation(img, "🟢 BAJA LATENCIA", 'top', 'green')

    # Convertir a numpy array
    frame = np.array(annotated)

    # Calcular número de frames para esta imagen
    duration = durations_seconds[slot]
    num_frames = int(duration * fps)

    # Agregar múltiples copias del frame según la duración
    for _ in range(num_frames):
        frames.append(frame)

    print(f"   ✅ Agregado: slot {slot} ({duration}s = {num_frames} frames)")

if frames:
    print(f"\n💾 Guardando video...")
    print(f"   Total frames: {len(frames)}")
    print(f"   FPS: {fps}")
    print(f"   Duración: {len(frames)/fps:.1f} segundos")

    # Guardar como MP4 con buena calidad
    iio.imwrite(
        output_file,
        frames,
        fps=fps,
        codec='libx264',
        quality=9,  # 0-10, donde 10 es la mejor calidad
        pixelformat='yuv420p',
        macro_block_size=16
    )

    file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB

    print(f"\n✅ Video MP4 creado exitosamente!")
    print(f"   📁 Archivo: {output_file}")
    print(f"   📊 Frames: {len(frames)}")
    print(f"   ⏱️  Duración: {len(frames)/fps:.1f}s")
    print(f"   💾 Tamaño: {file_size:.2f} MB")
    print(f"   🎬 FPS: {fps}")
    print(f"   🎨 Resolución: {frames[0].shape[1]}x{frames[0].shape[0]}")

    print(f"\n📊 Timeline del video:")
    print(f"   0:00-0:02   🔴 Alta latencia (slots 42-47)")
    print(f"   0:02-0:04   🔴 Máxima divergencia (slot 52)")
    print(f"   0:04-0:07   ⚡ TRANSICIÓN (slot 57)")
    print(f"   0:07-0:10   🟡 Primeros efectos (slots 62-67)")
    print(f"   0:10-0:12   🟢 Convergencia clara (slot 72)")
    print(f"   0:12-0:15   🟢 Estabilizado (slots 77-82)")

    print(f"\n🎥 Para ver el video:")
    print(f"   open {output_file}")
else:
    print("❌ No se encontraron imágenes para crear el video")

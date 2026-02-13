#!/usr/bin/env python3
"""Convierte el video de construcción a GIF para visualización"""
import imageio.v3 as iio
from PIL import Image

print("🎬 Convirtiendo video a GIF...")

# Leer video
video = iio.imread("visualizations/blockchain_construction.mp4")
print(f"   Video tiene {len(video)} frames")

# Para hacer el GIF más pequeño, tomar 1 de cada 3 frames
# y reducir resolución
frames_gif = []
step = 3  # Tomar 1 de cada 3 frames

for i in range(0, len(video), step):
    frame = Image.fromarray(video[i])
    # Reducir tamaño al 70% para GIF más liviano
    new_size = (int(frame.width * 0.7), int(frame.height * 0.7))
    frame_resized = frame.resize(new_size, Image.Resampling.LANCZOS)
    frames_gif.append(frame_resized)
    if i % 30 == 0:
        print(f"   Procesando frame {i}/{len(video)}")

print(f"\n💾 Guardando GIF...")
print(f"   Frames en GIF: {len(frames_gif)}")

# Guardar como GIF
output = "visualizations/blockchain_construction.gif"
frames_gif[0].save(
    output,
    save_all=True,
    append_images=frames_gif[1:],
    duration=100,  # 100ms por frame = 10 fps
    loop=0,
    optimize=False  # Más rápido sin optimizar
)

import os
size_mb = os.path.getsize(output) / (1024 * 1024)
print(f"\n✅ GIF creado: {output}")
print(f"   Tamaño: {size_mb:.2f} MB")
print(f"   Frames: {len(frames_gif)}")
print(f"   Duración: ~{len(frames_gif) * 0.1:.1f}s")

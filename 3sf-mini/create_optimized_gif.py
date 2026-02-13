#!/usr/bin/env python3
"""Crea un GIF optimizado del video de construcción"""
import imageio.v3 as iio
from PIL import Image

print("🎬 Creando GIF optimizado...")

video = iio.imread("visualizations/blockchain_construction.mp4")
print(f"   Video: {len(video)} frames")

frames_gif = []
step = 6  # Tomar 1 de cada 6 frames (5 fps)

for i in range(0, len(video), step):
    frame = Image.fromarray(video[i])
    # Reducir a 50% del tamaño
    new_size = (int(frame.width * 0.5), int(frame.height * 0.5))
    frame_resized = frame.resize(new_size, Image.Resampling.LANCZOS)
    # Convertir a paleta de 256 colores para GIF más pequeño
    frame_rgb = frame_resized.convert('RGB')
    frames_gif.append(frame_rgb)

print(f"   Frames para GIF: {len(frames_gif)}")

output = "visualizations/blockchain_construction_optimized.gif"
frames_gif[0].save(
    output,
    save_all=True,
    append_images=frames_gif[1:],
    duration=200,  # 200ms = 5 fps
    loop=0,
    optimize=True
)

import os
size_mb = os.path.getsize(output) / (1024 * 1024)
print(f"\n✅ GIF optimizado: {output}")
print(f"   Tamaño: {size_mb:.2f} MB")
print(f"   Frames: {len(frames_gif)}")

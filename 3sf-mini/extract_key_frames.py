#!/usr/bin/env python3
"""Extrae frames clave del video"""
import imageio.v3 as iio
from PIL import Image

video_file = "visualizations/latency_transition.mp4"

print("📸 Extrayendo frames clave del video...")

# Leer el video
video = iio.imread(video_file)
print(f"   Total frames en video: {len(video)}")

# Frames clave (aproximados)
# 30 fps, duraciones: 1s, 1s, 2s, 3s, 1.5s, 1.5s, 2s, 1s, 2s
key_frames = {
    15: "alta_latencia_slot42",      # Medio del slot 42
    45: "alta_latencia_slot47",      # Medio del slot 47
    90: "maxima_divergencia_slot52", # Medio del slot 52
    165: "transicion_slot57",        # Medio del slot 57 (MOMENTO CLAVE)
    240: "primeros_efectos_slot62",  # Medio del slot 62
    285: "mejora_slot67",            # Medio del slot 67
    330: "convergencia_slot72",      # Medio del slot 72
    375: "casi_lineal_slot77",       # Medio del slot 77
    420: "estabilizado_slot82",      # Medio del slot 82
}

for frame_idx, name in key_frames.items():
    if frame_idx < len(video):
        frame = video[frame_idx]
        output_file = f"visualizations/frame_{name}.png"
        img = Image.fromarray(frame)
        img.save(output_file)
        print(f"   ✅ Frame {frame_idx:3d}: {name}")
    else:
        print(f"   ⚠️  Frame {frame_idx} fuera de rango")

print(f"\n✅ Frames clave extraídos en: visualizations/frame_*.png")

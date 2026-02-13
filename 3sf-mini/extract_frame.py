#!/usr/bin/env python3
"""Extrae el frame del momento de transición del video"""
import imageio.v3 as iio
from PIL import Image

video_file = "visualizations/latency_transition.mp4"
output_file = "visualizations/video_preview_transition.png"

print("📸 Extrayendo frame del momento de transición...")

# Leer el video
video = iio.imread(video_file)

# El slot 57 (transición) debería estar alrededor del frame 120-210
# (0-60: slot 42, 60-120: slot 47, 120-180: slot 52, 180-270: slot 57)
transition_frame_idx = 210  # Medio del slot 57

if transition_frame_idx < len(video):
    frame = video[transition_frame_idx]
    img = Image.fromarray(frame)
    img.save(output_file)
    print(f"✅ Frame extraído: {output_file}")
    print(f"   Frame {transition_frame_idx}/{len(video)}")
    print(f"   Momento: Slot 57 - TRANSICIÓN")
else:
    print(f"❌ Frame {transition_frame_idx} fuera de rango (total: {len(video)})")

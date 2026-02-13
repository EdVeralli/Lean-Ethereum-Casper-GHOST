#!/usr/bin/env python3
import imageio.v3 as iio
from PIL import Image

video = iio.imread("visualizations/blockchain_construction.mp4")
# Frame del medio (slot 42 aprox)
frame_idx = len(video) // 2
frame = video[frame_idx]
Image.fromarray(frame).save("visualizations/construction_preview.png")
print(f"✅ Frame extraído: construction_preview.png (frame {frame_idx}/{len(video)})")

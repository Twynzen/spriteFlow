#!/usr/bin/env python3
"""
Script para crear un GIF de prueba desde las imagenes de test
"""

from PIL import Image
import os

# Leer las imágenes de prueba
img1 = Image.open('examples/inputs/test_start.png')
img2 = Image.open('examples/inputs/test_end.png')

# Crear frames intermedios simples (interpolación lineal)
frames = []
num_intermedios = 8

frames.append(img1)

# Crear frames intermedios con blend
for i in range(1, num_intermedios + 1):
    alpha = i / (num_intermedios + 1)
    frame = Image.blend(img1, img2, alpha)
    frames.append(frame)

frames.append(img2)

# Guardar como GIF
output_path = 'input/test_animation.gif'
os.makedirs('input', exist_ok=True)

frames[0].save(
    output_path,
    save_all=True,
    append_images=frames[1:],
    duration=100,  # 100ms por frame = 10fps
    loop=0
)

print(f'GIF de prueba creado: {output_path}')
print(f'Frames totales: {len(frames)}')
print(f'Duracion: {len(frames) * 0.1:.1f}s')

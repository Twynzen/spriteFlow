#!/usr/bin/env python3
"""
Script simple para crear imágenes de prueba
Genera 2 imágenes con un círculo en diferentes posiciones
"""

from PIL import Image, ImageDraw
import os

# Configuración
size = (512, 512)
circle_radius = 50
bg_color = (255, 255, 255)  # Blanco
circle_color = (255, 0, 0)  # Rojo

# Crear directorio
os.makedirs('examples/inputs', exist_ok=True)

# Imagen 1: Círculo a la izquierda
img1 = Image.new('RGB', size, bg_color)
draw1 = ImageDraw.Draw(img1)
circle1_pos = (150, 256)  # Izquierda, centro vertical
draw1.ellipse([
    circle1_pos[0] - circle_radius,
    circle1_pos[1] - circle_radius,
    circle1_pos[0] + circle_radius,
    circle1_pos[1] + circle_radius
], fill=circle_color)
img1.save('examples/inputs/test_start.png')
print('OK - Creada: examples/inputs/test_start.png')

# Imagen 2: Círculo a la derecha
img2 = Image.new('RGB', size, bg_color)
draw2 = ImageDraw.Draw(img2)
circle2_pos = (362, 256)  # Derecha, centro vertical
draw2.ellipse([
    circle2_pos[0] - circle_radius,
    circle2_pos[1] - circle_radius,
    circle2_pos[0] + circle_radius,
    circle2_pos[1] + circle_radius
], fill=circle_color)
img2.save('examples/inputs/test_end.png')
print('OK - Creada: examples/inputs/test_end.png')

print('')
print('EXITO - Imagenes de prueba creadas!')
print('El circulo se movera de izquierda a derecha')

# SpriteFlow Examples

Esta carpeta contiene archivos de ejemplo para empezar a usar SpriteFlow.

## Archivos

### `batch_config_example.json`

Archivo de configuración de ejemplo para procesamiento por lotes.

**Estructura:**
```json
{
  "rembg_model": "u2net",
  "rife_model": "train_log/flownet.pkl",
  "animations": [
    {
      "name": "nombre_animacion",
      "start": "ruta/imagen_inicio.png",
      "end": "ruta/imagen_fin.png",
      "frames": 30,
      "remove_bg": true
    }
  ]
}
```

**Campos:**
- `rembg_model`: Modelo para remover fondo (u2net, isnet-anime, birefnet-general)
- `rife_model`: Path al modelo RIFE
- `animations`: Array de animaciones a procesar
  - `name`: Nombre identificador de la animación
  - `start`: Path a imagen inicial (keyframe A)
  - `end`: Path a imagen final (keyframe B)
  - `frames`: Número de frames intermedios a generar (default: 30)
  - `remove_bg`: Si remover fondo automáticamente (default: true)

## Carpeta `inputs/`

Coloca tus imágenes de entrada aquí.

**Recomendaciones:**
- Formato: PNG (preferiblemente con transparencia)
- Tamaño: 512x512 a 1024x1024 pixels
- Nombres claros: `walk_right_start.png`, `walk_right_end.png`
- Poses similares entre start/end para mejor interpolación

**Estructura recomendada:**
```
inputs/
├── walk_right_start.png
├── walk_right_end.png
├── attack_start.png
├── attack_end.png
├── idle_start.png
├── idle_end.png
└── batch_config.json
```

## Uso Rápido

1. **Copiar el ejemplo:**
   ```bash
   cp batch_config_example.json batch_config.json
   ```

2. **Editar paths en batch_config.json** para que apunten a tus imágenes

3. **Colocar tus imágenes en `inputs/`**

4. **Procesar:**
   ```bash
   python src/batch_process.py examples/batch_config.json
   ```

5. **Ver resultados en `batch_output/`**

## Tips

- **Empezar pequeño**: Procesa 2-3 animaciones primero para verificar
- **Naming consistente**: Usa sufijos `_start.png` y `_end.png`
- **Test local**: Si tienes GPU, prueba localmente antes de subir a cloud
- **Documentar**: Mantén un log de qué animaciones procesaste cada semana

## Troubleshooting

**Error: "Image not found"**
- Verifica que los paths en batch_config.json sean correctos
- Los paths son relativos al directorio donde ejecutas el script

**Error: "Different image sizes"**
- Las imágenes start y end deben tener el mismo tamaño
- Usa ImageMagick para redimensionar: `mogrify -resize 512x512 *.png`

**Resultados extraños:**
- Verifica que las poses start/end sean similares
- Revisa que las imágenes no estén corruptas
- Prueba con menos frames primero (15 en vez de 30)

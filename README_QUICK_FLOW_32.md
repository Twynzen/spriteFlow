# 🎮 Quick Flow 32 - Loop Perfecto Garantizado

> **Flujo especial:** MP4 → 32 Looping Sprites → Spritesheet automático

## ✨ ¿Qué hace?

Convierte videos MP4 en exactamente **32 sprites** con **loop perfecto garantizado**, ideal para animaciones cíclicas en videojuegos (walk, run, idle, etc.).

### 🎯 Características Únicas

✅ **Loop Perfecto Matemático**
- Frame 32 es idéntico a Frame 1
- Cuando el loop se repite, no hay saltos visuales
- Perfecto para walk cycles, idle animations, etc.

✅ **Sin IA - Funciona en Mac**
- Color Key (chromakey) para remover fondos
- No requiere CUDA/GPU
- Solo necesita FFmpeg + Python

✅ **Automatización Completa**
- Un solo comando/script
- Genera sprites individuales + spritesheet
- Metadata JSON incluido

✅ **Optimizado para Game Engines**
- 32 frames = potencia de 2
- Spritesheet 8x4 (8 columnas × 4 filas)
- Formato PNG con alpha channel

---

## 🚀 Uso Rápido

### **Opción 1: Modo Interactivo (Recomendado)**

```bash
# 1. Coloca tu video MP4 en la carpeta input/
cp mi_animacion.mp4 input/

# 2. Ejecuta el quick flow
python quick_flow_32.py

# 3. Sigue las instrucciones en pantalla
```

### **Opción 2: Línea de Comandos**

```bash
python src/mp4_to_looping_sprites.py \
  --input input/walk_cycle.mp4 \
  --output output \
  --name hero-walk \
  --frames 32 \
  --color-key black \
  --tolerance 30
```

---

## 📋 Workflow Detallado

### **Paso 1: Preparar Video**

Coloca un video MP4 en la carpeta `input/`:

```
spriteFlow/
├── input/
│   └── walk_cycle.mp4  ← Tu video aquí
└── output/
    └── (vacío)
```

**Requisitos del video:**
- Formato: MP4, MOV, AVI (FFmpeg compatible)
- Fondo: Color sólido (negro, blanco, o verde recomendado)
- Duración: Cualquiera (se extrae un ciclo completo)
- Resolución: Cualquiera

### **Paso 2: Ejecutar Quick Flow**

```bash
python quick_flow_32.py
```

**El script te preguntará:**

1. **Nombre base para sprites**
   - Ejemplo: `hero-walk`
   - Resultado: `hero-walk-001.png`, `hero-walk-002.png`, ..., `hero-walk-032.png`

2. **Color de fondo a remover**
   - `[1]` Negro (default)
   - `[2]` Blanco
   - `[3]` Verde (chroma)

3. **Tolerancia color key** (0-255)
   - Menor = más estricto (solo colores muy exactos)
   - Mayor = más permisivo (colores similares)
   - Default: 30

4. **¿Recortar bordes?** (opcional)
   - Para eliminar watermarks en esquinas
   - Ejemplo: `40` = recorta 40px de cada lado

5. **¿Generar spritesheet?**
   - `S` (default): Sí, crear spritesheet 8x4
   - `n`: No, solo sprites individuales

### **Paso 3: Resultados**

```
output/
├── hero-walk-001.png    ← Sprites individuales
├── hero-walk-002.png
├── ...
├── hero-walk-032.png
├── hero-walk_spritesheet.png      ← Spritesheet 8x4
└── hero-walk_spritesheet.json     ← Metadata
```

---

## 🔧 Cómo Funciona el Loop Perfecto

### **Estrategia: Copiar Frame 0 como Frame 31**

```
Video MP4 (100 frames)
     ↓
Extrae 31 frames equidistantes [0, 3, 6, 9, ..., 99]
     ↓
Copia frame 0 como frame 31
     ↓
Total: 32 frames donde frame[31] == frame[0]
     ↓
Loop seamless garantizado
```

### **Ejemplo Práctico: Walk Cycle**

**Video original:**
```
Frame 0:  Pie izq adelante
Frame 10: Ambos pies juntos
Frame 20: Pie der adelante
Frame 30: Ambos pies juntos
Frame 40: Pie izq adelante  ← Similar a frame 0
...
```

**Extracción (31 frames únicos):**
```
Sprite 1:  Frame 0  (pie izq adelante)
Sprite 8:  Frame 10 (pies juntos)
Sprite 15: Frame 20 (pie der adelante)
Sprite 22: Frame 30 (pies juntos)
Sprite 31: Frame 40 (pie izq adelante, cercano a frame 0)
```

**Loop forzado:**
```
Sprite 32: Copia exacta de Sprite 1
```

**Resultado:**
```
Cuando el juego reproduce sprites 1-32 en loop:
Sprite 32 → Sprite 1 es una transición perfecta (mismo frame)
No hay saltos visuales
```

---

## 🎨 Ejemplos de Uso

### **Ejemplo 1: Walk Cycle Básico**

```bash
# Video: personaje caminando con fondo negro
python quick_flow_32.py

# Configuración:
#   Nombre: hero-walk-right
#   Color Key: Negro (1)
#   Tolerancia: 30
#   Crop: No
#   Spritesheet: Sí
```

**Resultado:**
- 32 sprites con fondo transparente
- Loop perfecto cuando el personaje vuelve a la pose inicial
- Spritesheet listo para Unity/Godot/Phaser

### **Ejemplo 2: Run Cycle con Watermark**

```bash
# Video: personaje corriendo, watermark en esquina superior derecha
python quick_flow_32.py

# Configuración:
#   Nombre: hero-run-left
#   Color Key: Blanco (2)
#   Tolerancia: 50
#   Crop: 40  ← Recorta 40px de todos los lados
#   Spritesheet: Sí
```

**Resultado:**
- Watermark eliminado
- Fondo blanco removido
- Loop perfecto

### **Ejemplo 3: Idle Animation**

```bash
# Video: personaje parado respirando (movimiento sutil)
python quick_flow_32.py

# Configuración:
#   Nombre: hero-idle
#   Color Key: Verde (3) ← Chroma key verde
#   Tolerancia: 40
#   Crop: No
#   Spritesheet: Sí
```

---

## 📊 Metadata JSON

El archivo `{nombre}_spritesheet.json` contiene:

```json
{
  "name": "hero-walk",
  "frameWidth": 128,
  "frameHeight": 128,
  "frameCount": 32,
  "columns": 8,
  "rows": 4,
  "padding": 0,
  "totalWidth": 1024,
  "totalHeight": 512
}
```

**Uso en game engines:**

```javascript
// Phaser 3
this.load.spritesheet('hero-walk', 'hero-walk_spritesheet.png', {
  frameWidth: 128,
  frameHeight: 128
});

// Unity C#
// Importar como Sprite Atlas, configurar grid 8x4

// Godot
// AnimatedSprite con SpriteFrames de 32 frames
```

---

## ⚙️ Configuración Avanzada

### **Color Key Personalizado**

Para colores específicos (no negro/blanco/verde):

```python
# Editar src/mp4_to_looping_sprites.py
processor = MP4ToLoopingSpriteProcessor(
    color_key_color=(255, 0, 255),  # Magenta RGB
    color_key_tolerance=30
)
```

### **Número de Frames Diferente**

Si necesitas 16, 24, 64 frames en lugar de 32:

```bash
python src/mp4_to_looping_sprites.py \
  --input input/video.mp4 \
  --frames 16  # ← Cambia aquí
```

### **Deshabilitar Loop Forzado**

Si tu video ya es perfectamente cíclico:

```bash
python src/mp4_to_looping_sprites.py \
  --input input/video.mp4 \
  --no-loop  # No copia frame 0 como último
```

---

## 🔍 Troubleshooting

### **"FFmpeg no encontrado"**

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Debian/Ubuntu
sudo pacman -S ffmpeg    # Arch
```

**Windows:**
```bash
winget install ffmpeg
# o
choco install ffmpeg
```

### **"Fondo no se remueve completamente"**

1. **Aumenta tolerancia:**
   Color Key tolerance 30 → 50

2. **Verifica color de fondo:**
   Asegúrate de seleccionar el color correcto (negro/blanco/verde)

3. **Iluminación uniforme:**
   Videos con sombras o gradientes necesitan mayor tolerancia

### **"Loop tiene un pequeño salto"**

**Causas comunes:**
- El video original no es cíclico (ej: ataque, salto)
- El video tiene demasiados frames y la distribución no captura el ciclo completo

**Soluciones:**
1. Recorta el video para incluir solo UN ciclo completo
2. Usa `--no-loop` si el video ya es perfectamente cíclico
3. Edita manualmente el último frame para que coincida con el primero

### **"Spritesheet muy grande"**

```bash
# Reducir resolución del video antes de procesar
ffmpeg -i input.mp4 -vf scale=512:512 input_small.mp4
```

---

## 🎯 Casos de Uso

### **Game Development**
- Walk/Run cycles para plataformers
- Idle animations para RPGs
- Enemy patrol animations
- Item rotation animations

### **Animation**
- Animatics y previsualización
- Loop GIFs para redes sociales
- Motion graphics cíclicos

### **NFT Projects**
- Avatar animations
- Generative art con movimiento
- Pfp collections animadas

---

## 🚀 Próximas Mejoras

- [ ] Detección automática de ciclo en el video
- [ ] Preview del loop antes de procesar
- [ ] Batch processing de múltiples MP4s
- [ ] Optimización de tamaño de sprites
- [ ] Export directo a formatos de game engines

---

## 📄 Licencia

MIT License - Úsalo libremente en proyectos personales y comerciales.

---

**¿Listo para crear sprites con loop perfecto?**

```bash
python quick_flow_32.py
```

🎮 ¡Haz que tus animaciones fluyan sin saltos!

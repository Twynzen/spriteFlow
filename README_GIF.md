# 🎨 SpriteFlow - GIF to Sprites Processor

> **Nueva Funcionalidad:** Convierte GIFs animados en sprites individuales con fondo removido automáticamente

---

## 🚀 Guía de Uso Rápida

### **Paso 1: Activar entorno**
```bash
.venv\Scripts\activate
```

### **Paso 2: Ejecutar menú**
```bash
python spriteflow_menu.py
```

### **Paso 3: Colocar GIF en carpeta `input/`**
```
spriteFlow/
├── input/
│   └── tu_animacion.gif  ← Coloca tu GIF aquí
└── output/
    └── (sprites se generan aquí)
```

### **Paso 4: Seleccionar opción [1] en el menú**

El sistema te preguntará:
1. **Cuántos frames quieres extraer** (ej: 10, 20, 30)
2. **Nombre base para los archivos** (ej: `hero-walk-right`)

### **Paso 5: Los sprites aparecen en `output/`**
```
output/
├── hero-walk-right-001.png
├── hero-walk-right-002.png
├── hero-walk-right-003.png
└── ...
```

---

## 📋 Ejemplo de Flujo Completo

```
============================================================
    SPRITEFLOW - GIF a Sprites (Fondo Removido)
============================================================

MENU:
============================================================
  [1] Procesar GIF a Sprites (con fondo removido)
  [2] Ver estado de carpetas input/output
  [3] Informacion del sistema
  [0] Salir
============================================================

Selecciona opcion: 1

GIF detectado: warrior_animation.gif

Informacion del GIF:
============================================================
  Duracion:       2.50s
  Frames totales: 75
  FPS:            30.0
  Resolucion:     512x512
============================================================

Cuantos frames quieres extraer?
(Maximo disponible: 75)
Numero de frames [30]: 10

============================================================
NOMBRE DE ARCHIVOS
============================================================
Los sprites se guardaran con el formato:
  {nombre_base}-001.png
  {nombre_base}-002.png
  ...

Ejemplos de nombres base:
  hero-walk-right
  enemy-attack-left
  player-jump
============================================================

Ingresa nombre base [sprite]: warrior-walk

============================================================
RESUMEN DEL PROCESAMIENTO
============================================================
  GIF:              warrior_animation.gif
  Frames a extraer: 10
  Nombre base:      warrior-walk-###.png
  Remover fondo:    SI (automatico)
  Carpeta salida:   output/
============================================================

Iniciar procesamiento? (s/n) [s]: s

============================================================
PROCESANDO...
============================================================

Inicializando GIF Processor en cuda...
Cargando rembg (u2net)...
Procesador listo!

Extrayendo 10 frames de 75 totales...
Indices seleccionados: [0, 8, 16, 25, 33, 41, 50, 58, 66, 74]
Frames extraidos exitosamente!

Removiendo fondos...
  Frame 1/10: Procesando... OK - warrior-walk-001.png
  Frame 2/10: Procesando... OK - warrior-walk-002.png
  Frame 3/10: Procesando... OK - warrior-walk-003.png
  ...
  Frame 10/10: Procesando... OK - warrior-walk-010.png

============================================================
PROCESAMIENTO COMPLETADO
============================================================
  Frames procesados: 10/10
  Tiempo total:      45.23s
  Tiempo por frame:  4.52s
  Directorio:        output
============================================================

EXITO! SPRITES GENERADOS

Los sprites estan en:
  C:\...\spriteFlow\output

Archivos generados:
  1. warrior-walk-001.png
  2. warrior-walk-002.png
  3. warrior-walk-003.png
  4. warrior-walk-004.png
  5. warrior-walk-005.png
  ... y 5 archivos mas

Total: 10 sprites
```

---

## 🎯 Características

### ✅ **Extracción Inteligente de Frames**
- Selecciona frames **equidistantes** del GIF
- Si pides 10 frames de un GIF con 100 frames, toma 1 cada 10
- Distribución uniforme en el tiempo

### ✅ **Remoción Automática de Fondo**
- Usa modelo **U2-Net** pre-entrenado
- Procesamiento **GPU-acelerado** (RTX 3070)
- Mantiene transparencia (formato PNG con canal alpha)

### ✅ **Nombres Personalizables**
- Formato: `{nombre_base}-###.png`
- Ejemplos:
  - `hero-walk-right-001.png`
  - `enemy-attack-left-015.png`
  - `player-jump-008.png`

### ✅ **Sin Límites de Uso**
- **$0 de costo** (todo local)
- Procesa cuantos GIFs quieras
- Sin dependencia de APIs externas

---

## 📊 Rendimiento

### **Hardware usado:**
- GPU: NVIDIA RTX 3070
- CPU: Variable
- RAM: ~4GB durante procesamiento

### **Tiempos estimados:**

| Frames extraídos | Tiempo total | Tiempo/frame |
|-----------------|--------------|--------------|
| 10 frames       | ~45s         | ~4.5s        |
| 20 frames       | ~90s         | ~4.5s        |
| 30 frames       | ~135s        | ~4.5s        |

*Nota: Tiempo por frame es constante (~4-5s), ya que cada uno pasa por rembg individualmente*

---

## 🛠️ Uso Avanzado (Línea de Comandos)

Si prefieres no usar el menú interactivo:

```bash
python src/process_gif.py \
  --gif input/mi_animacion.gif \
  --frames 20 \
  --name hero-walk-right \
  --output output
```

**Parámetros:**
- `--gif`: Path al archivo GIF
- `--frames`: Número de frames a extraer (default: 30)
- `--name`: Nombre base para archivos (default: sprite)
- `--output`: Directorio de salida (default: output)
- `--rembg-model`: Modelo rembg (u2net, isnet-anime, birefnet-general)

---

## 🤔 FAQ

### **P: ¿Qué pasa si pido más frames de los que tiene el GIF?**
**R:** El sistema extrae todos los frames disponibles y te avisa.

### **P: ¿Puedo procesar múltiples GIFs a la vez?**
**R:** Actualmente procesa un GIF a la vez. Si hay varios en `input/`, usa el primero alfabéticamente.

### **P: ¿Qué formatos de imagen soporta la salida?**
**R:** Solo PNG con canal alpha (transparencia).

### **P: ¿Puedo desactivar la remoción de fondo?**
**R:** No en esta versión. El propósito es generar sprites con fondo removido.

### **P: ¿Qué calidad tienen los sprites generados?**
**R:** Mantienen la resolución original del GIF. La calidad del fondo removido depende del modelo U2-Net.

---

## 🔧 Troubleshooting

### **Error: "No se encontro ningun GIF"**
- Verifica que el archivo esté en la carpeta `input/`
- Verifica que la extensión sea `.gif` (minúsculas)

### **Error: "CUDA out of memory"**
- Reduce el número de frames a extraer
- Cierra otras aplicaciones que usen GPU
- Usa un GIF de menor resolución

### **Procesamiento muy lento**
- Verifica que CUDA esté disponible (opción [3] del menú)
- Si usa CPU, el procesamiento será ~10x más lento

---

## 📁 Estructura del Proyecto

```
spriteFlow/
├── input/                  # Coloca tus GIFs aquí
│   └── test_animation.gif  # GIF de prueba incluido
├── output/                 # Sprites generados
│   ├── sprite-001.png
│   ├── sprite-002.png
│   └── ...
├── src/
│   └── process_gif.py      # Motor de procesamiento
├── spriteflow_menu.py      # Menú interactivo
├── create_test_gif.py      # Crear GIF de prueba
└── README_GIF.md           # Esta documentación
```

---

## 🎮 Casos de Uso

1. **Desarrollo de videojuegos**
   - Extraer sprites de animaciones de referencia
   - Procesar walk cycles, ataques, saltos, etc.

2. **Pixel art**
   - Convertir animaciones en frames individuales
   - Editar frame por frame después

3. **Asset packs**
   - Preparar sprites para venta/distribución
   - Formato estándar con fondos removidos

4. **Prototipado rápido**
   - Usar animaciones existentes como placeholder
   - Testear movimientos antes de crear arte final

---

## 📝 Notas Técnicas

### **¿Cómo funciona la extracción equidistante?**

Si tienes un GIF con **100 frames** y pides **10 frames**:

```python
step = (100 - 1) / (10 - 1) = 11
indices = [0, 11, 22, 33, 44, 55, 66, 77, 88, 99]
```

Esto asegura que los frames estén **uniformemente distribuidos** en el tiempo.

### **¿Por qué rembg y no otro método?**

- **U2-Net** es el estado del arte para remoción de fondos
- **GPU-acelerado** (usa tu RTX 3070)
- **Open source** y gratis
- **Resultados consistentes** para sprites

---

## 🚀 Próximas Mejoras

- [ ] Soporte para múltiples GIFs en batch
- [ ] Opción de desactivar remoción de fondo
- [ ] Exportar spritesheet (grid de sprites)
- [ ] Vista previa antes de procesar
- [ ] Ajuste de brillo/contraste

---

## 📄 Licencia

MIT License - Úsalo libremente para proyectos personales y comerciales.

---

**¿Listo para probar?**

```bash
.venv\Scripts\activate
python spriteflow_menu.py
```

¡Y selecciona opción [1]!

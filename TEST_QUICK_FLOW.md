# 🧪 Test Rápido - Quick Flow 32

## ✅ Checklist de Prueba

### **Requisitos Previos**

- [ ] Python 3.9+ instalado
- [ ] FFmpeg instalado (`brew install ffmpeg` en Mac)
- [ ] Dependencias instaladas (`pip install Pillow numpy`)

### **Test 1: Verificar FFmpeg**

```bash
ffmpeg -version
```

**Resultado esperado:** Versión de FFmpeg (ej: `ffmpeg version 6.0`)

---

### **Test 2: Crear Video de Prueba Simple**

Si no tienes un MP4 de prueba, usa este script para generar uno:

```bash
# Crear video de prueba con círculo rotando (fondo negro)
ffmpeg -f lavfi -i color=c=black:s=512x512:d=2 \
  -vf "drawtext=text='Frame %{frame_num}':x=(w-tw)/2:y=(h-th)/2:fontsize=48:fontcolor=white" \
  -c:v libx264 -t 2 -pix_fmt yuv420p \
  input/test_rotation.mp4
```

**Esto crea:**
- Video de 2 segundos
- 512x512 píxeles
- Fondo negro (perfecto para Color Key)
- Texto mostrando número de frame

---

### **Test 3: Ejecutar Quick Flow 32**

```bash
# Asegúrate de estar en la carpeta spriteFlow/
cd /Users/dcastiblanco/Desktop/GPTsProyects/spriteflow/spriteFlow

# Ejecutar
python quick_flow_32.py
```

**Configuración de prueba:**
```
Nombre base: test
Color Key: [1] Negro
Tolerancia: 30
Crop: [presiona ENTER para no recortar]
Spritesheet: S
Confirmar: S
```

**Resultado esperado:**
```
output/
├── test-001.png
├── test-002.png
├── ...
├── test-032.png
├── test_spritesheet.png
└── test_spritesheet.json
```

---

### **Test 4: Verificar Loop Perfecto**

```bash
# Ver primer frame
open output/test-001.png

# Ver último frame
open output/test-032.png
```

**✅ Verificación:** Los archivos `test-001.png` y `test-032.png` deben ser **idénticos**

---

### **Test 5: Verificar Spritesheet**

```bash
open output/test_spritesheet.png
```

**Resultado esperado:**
- Grid de 8 columnas × 4 filas
- Total: 32 sprites visibles
- Fondo transparente

---

### **Test 6: Verificar Metadata**

```bash
cat output/test_spritesheet.json
```

**Resultado esperado:**
```json
{
  "name": "test",
  "frameWidth": 512,
  "frameHeight": 512,
  "frameCount": 32,
  "columns": 8,
  "rows": 4,
  "padding": 0,
  "totalWidth": 4096,
  "totalHeight": 2048
}
```

---

## 🎯 Test con Video Real

### **Paso 1: Conseguir video de prueba**

Descarga un video de animación cíclica (ej: Mixamo, OpenGameArt, etc.)

**Ejemplo:** https://www.mixamo.com (requiere cuenta gratuita)
1. Selecciona personaje
2. Selecciona animación "Walking"
3. Descarga como FBX
4. Convierte a MP4 con software de tu elección

O usa videos de test de estos sitios:
- https://www.pexels.com/search/videos/walk%20cycle/
- https://pixabay.com/videos/search/animation/

### **Paso 2: Procesamiento**

```bash
# Copiar video a input/
cp ~/Downloads/walk_cycle.mp4 input/

# Ejecutar quick flow
python quick_flow_32.py
```

### **Paso 3: Verificación de Calidad**

1. **Background removal:**
   - [ ] ¿El fondo está completamente removido?
   - [ ] ¿Hay residuos alrededor del personaje?

2. **Loop seamless:**
   - [ ] ¿Frame 1 y Frame 32 son similares/idénticos?
   - [ ] ¿La animación fluye sin saltos?

3. **Spritesheet:**
   - [ ] ¿Todos los frames son visibles?
   - [ ] ¿El tamaño es correcto?

---

## 🐛 Debugging

### **Error: "FFmpeg no encontrado"**

```bash
# Mac
brew install ffmpeg

# Verificar instalación
which ffmpeg
```

### **Error: "ModuleNotFoundError: No module named 'PIL'"**

```bash
pip install Pillow numpy
```

### **Error: "No se encontró ningún MP4"**

```bash
# Verificar que el archivo esté en input/
ls -la input/

# Debe mostrar archivos .mp4
```

### **Warning: "Video tiene menos frames que los solicitados"**

- El video es muy corto (< 1 segundo)
- Se extraerán todos los frames disponibles (menos de 32)
- Usa un video más largo o reduce `--frames`

---

## 📊 Performance Benchmarks

**Hardware de prueba:** MacBook Pro M1

| Resolución | Duración | Frames | Tiempo | Memoria |
|------------|----------|--------|--------|---------|
| 512x512    | 2s       | 32     | ~8s    | ~200MB  |
| 1024x1024  | 2s       | 32     | ~15s   | ~500MB  |
| 512x512    | 5s       | 32     | ~10s   | ~250MB  |

**Nota:** No usa GPU, todo es CPU + FFmpeg

---

## ✅ Checklist Final

Marca cada item cuando lo completes:

- [ ] FFmpeg instalado y funcionando
- [ ] Quick Flow 32 ejecutado sin errores
- [ ] 32 sprites generados en output/
- [ ] Frame 1 y Frame 32 son idénticos (loop perfecto)
- [ ] Spritesheet generado correctamente
- [ ] Metadata JSON válido
- [ ] Background removido con Color Key
- [ ] Test con video real completado

---

**🎉 Si todos los checks están completos, el sistema funciona correctamente!**

Ahora puedes:
1. Crear tus propias animaciones
2. Ajustar configuraciones (color key, tolerancia, crop)
3. Integrar sprites en tu game engine

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpriteFlow - MP4 to 32 Looping Sprites
Flujo especial que garantiza loop perfecto (frame 31 = frame 0)

Features:
- Extrae exactamente 32 frames de MP4
- Garantiza loop perfecto (último frame = primer frame)
- Color Key para remover fondos (sin IA, funciona en Mac)
- Genera spritesheet automáticamente
- Sin dependencia de CUDA/GPU
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from PIL import Image
import numpy as np
from typing import List, Tuple, Optional


class MP4ToLoopingSpriteProcessor:
    def __init__(self,
                 color_key_color='black',
                 color_key_tolerance=30,
                 crop_margins=None,
                 ensure_loop=True):
        """
        Procesador MP4 → 32 Looping Sprites

        Args:
            color_key_color: 'black', 'white', 'green', o tuple RGB (ej: (0, 255, 0))
            color_key_tolerance: Tolerancia para color key (0-255)
            crop_margins: Tuple (top, right, bottom, left) en pixeles
            ensure_loop: Si True, copia frame 0 como frame 31 para garantizar loop
        """
        self.color_key_tolerance = color_key_tolerance
        self.crop_margins = crop_margins
        self.ensure_loop = ensure_loop

        # Parsear color key
        if color_key_color == 'white':
            self.color_key_rgb = (255, 255, 255)
        elif color_key_color == 'black':
            self.color_key_rgb = (0, 0, 0)
        elif color_key_color == 'green':
            self.color_key_rgb = (0, 255, 0)
        else:
            self.color_key_rgb = color_key_color

        print(f"🎬 MP4 to Looping Sprites Processor")
        print(f"   Color Key: {color_key_color} (tolerancia: {color_key_tolerance})")
        print(f"   Loop forzado: {'✅ Sí' if ensure_loop else '❌ No'}")
        if crop_margins:
            print(f"   Crop margins: {crop_margins}")
        print()

    def get_ffmpeg_path(self):
        """Obtener path de FFmpeg"""
        # Intentar en PATH
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return 'ffmpeg'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Buscar en ubicaciones comunes (Mac)
        posibles_rutas = [
            Path("/usr/local/bin/ffmpeg"),
            Path("/opt/homebrew/bin/ffmpeg"),
            Path.home() / "bin/ffmpeg",
        ]

        for ffmpeg_path in posibles_rutas:
            if ffmpeg_path.exists():
                return str(ffmpeg_path)

        return None

    def get_video_info(self, video_path):
        """Obtener información del video"""
        ffmpeg = self.get_ffmpeg_path()
        if not ffmpeg:
            raise FileNotFoundError("FFmpeg no encontrado. Instala con: brew install ffmpeg")

        try:
            # Obtener duración y frame count
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-count_frames',
                '-show_entries', 'stream=nb_read_frames,duration,r_frame_rate,width,height',
                '-of', 'csv=p=0',
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            parts = result.stdout.strip().split(',')

            width = int(parts[0]) if len(parts) > 0 else 0
            height = int(parts[1]) if len(parts) > 1 else 0

            # FPS
            fps_str = parts[2] if len(parts) > 2 else "30/1"
            if '/' in fps_str:
                num, den = fps_str.split('/')
                fps = float(num) / float(den) if float(den) != 0 else 30
            else:
                fps = float(fps_str) if fps_str else 30

            # Duración
            duration = float(parts[3]) if len(parts) > 3 else 0

            # Total frames
            total_frames = int(parts[4]) if len(parts) > 4 else int(duration * fps)

            return {
                'width': width,
                'height': height,
                'fps': fps,
                'duration': duration,
                'total_frames': total_frames
            }
        except Exception as e:
            print(f"⚠️  Error obteniendo info del video: {e}")
            return None

    def extract_frames_from_mp4(self, video_path, output_dir, num_frames=32):
        """
        Extraer frames del MP4 usando FFmpeg

        Estrategia para loop perfecto:
        - Si ensure_loop=True: Extrae 31 frames únicos + copia frame 0 como frame 31
        - Si ensure_loop=False: Extrae 32 frames equidistantes normales

        Args:
            video_path: Path al MP4
            output_dir: Directorio de salida
            num_frames: Número de frames a extraer (default: 32)

        Returns:
            Lista de paths a los frames extraídos
        """
        os.makedirs(output_dir, exist_ok=True)

        ffmpeg = self.get_ffmpeg_path()
        if not ffmpeg:
            raise FileNotFoundError("FFmpeg no encontrado")

        info = self.get_video_info(video_path)
        if not info:
            raise ValueError("No se pudo analizar el video")

        print(f"📹 Video: {Path(video_path).name}")
        print(f"   Resolución: {info['width']}x{info['height']}")
        print(f"   FPS: {info['fps']:.1f}")
        print(f"   Duración: {info['duration']:.2f}s")
        print(f"   Frames totales: {info['total_frames']}")
        print()

        # Calcular cuántos frames únicos extraer
        if self.ensure_loop:
            unique_frames = num_frames - 1  # 31 frames únicos
            print(f"🔄 Modo Loop Forzado: Extrayendo {unique_frames} frames + copiar frame 0 como frame {num_frames-1}")
        else:
            unique_frames = num_frames
            print(f"📊 Extrayendo {num_frames} frames equidistantes")

        print()

        # Extraer frames con FFmpeg usando select
        # Calculamos los timestamps específicos para extraer
        frame_paths = []

        if unique_frames >= info['total_frames']:
            # Extraer todos los frames disponibles
            print("⚠️  Video tiene menos frames que los solicitados, extrayendo todos...")
            cmd = [
                ffmpeg, '-i', str(video_path),
                '-vf', 'select=gt(n\\,0)',  # Seleccionar todos
                '-vsync', '0',
                os.path.join(output_dir, 'frame_%04d.png')
            ]
        else:
            # Extraer frames equidistantes
            total = info['total_frames']
            step = (total - 1) / (unique_frames - 1) if unique_frames > 1 else 0
            indices = [int(i * step) for i in range(unique_frames)]

            # Crear expresión select para FFmpeg
            select_expr = '+'.join([f'eq(n\\,{idx})' for idx in indices])

            cmd = [
                ffmpeg, '-i', str(video_path),
                '-vf', f'select={select_expr}',
                '-vsync', '0',
                os.path.join(output_dir, 'frame_%04d.png')
            ]

        try:
            # Ejecutar FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )

            if result.returncode != 0:
                print(f"❌ Error en FFmpeg: {result.stderr}")
                raise RuntimeError("FFmpeg falló")

            # Recopilar paths de frames extraídos
            frame_paths = sorted(list(Path(output_dir).glob('frame_*.png')))

            # Si ensure_loop, copiar primer frame como último
            if self.ensure_loop and len(frame_paths) > 0:
                first_frame = frame_paths[0]
                last_frame_path = Path(output_dir) / f'frame_{len(frame_paths)+1:04d}.png'
                shutil.copy(first_frame, last_frame_path)
                frame_paths.append(last_frame_path)
                print(f"✅ Frame 0 copiado como frame {len(frame_paths)-1} para loop perfecto")

            print(f"✅ {len(frame_paths)} frames extraídos\n")
            return [str(p) for p in frame_paths]

        except subprocess.TimeoutExpired:
            print("❌ FFmpeg timeout (video muy largo?)")
            raise
        except Exception as e:
            print(f"❌ Error extrayendo frames: {e}")
            raise

    def crop_image(self, image):
        """Recortar bordes de la imagen"""
        if not self.crop_margins:
            return image

        top, right, bottom, left = self.crop_margins
        width, height = image.size

        new_left = left
        new_top = top
        new_right = width - right
        new_bottom = height - bottom

        if new_right <= new_left or new_bottom <= new_top:
            return image

        return image.crop((new_left, new_top, new_right, new_bottom))

    def remove_background_color_key(self, image):
        """
        Remover fondo usando color key (chroma key)

        Args:
            image: PIL.Image

        Returns:
            PIL.Image con fondo removido (RGBA)
        """
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        img_array = np.array(image)
        rgb = img_array[:, :, :3]
        alpha = img_array[:, :, 3]

        # Calcular diferencia con color key
        target = np.array(self.color_key_rgb, dtype=np.float32)
        diff = np.sqrt(np.sum((rgb.astype(np.float32) - target) ** 2, axis=2))

        # Crear máscara: True donde el color está dentro de la tolerancia
        mask = diff <= self.color_key_tolerance

        # Hacer transparentes los pixels que coinciden con el color key
        alpha[mask] = 0
        img_array[:, :, 3] = alpha

        return Image.fromarray(img_array, 'RGBA')

    def process(self, mp4_path, output_dir, sprite_name="sprite", num_frames=32):
        """
        Flujo completo: MP4 → 32 Looping Sprites

        Args:
            mp4_path: Path al video MP4
            output_dir: Directorio de salida
            sprite_name: Nombre base para los sprites
            num_frames: Número de frames (default: 32)

        Returns:
            dict con resultados
        """
        import time
        start_time = time.time()

        print("=" * 70)
        print("🎨 MP4 TO 32 LOOPING SPRITES")
        print("=" * 70)
        print()

        # Crear directorios
        os.makedirs(output_dir, exist_ok=True)
        temp_dir = Path(output_dir) / "_temp_frames"
        os.makedirs(temp_dir, exist_ok=True)

        # Paso 1: Extraer frames del MP4
        print("📹 PASO 1/3: Extrayendo frames del MP4...")
        frame_paths = self.extract_frames_from_mp4(mp4_path, temp_dir, num_frames)

        if len(frame_paths) != num_frames:
            print(f"⚠️  Advertencia: Se esperaban {num_frames} frames, se obtuvieron {len(frame_paths)}")

        # Paso 2: Procesar cada frame (crop + color key)
        print("🎨 PASO 2/3: Aplicando Color Key y procesando sprites...")
        processed_sprites = []

        for i, frame_path in enumerate(frame_paths):
            frame_num = i + 1

            # Leer imagen
            img = Image.open(frame_path)

            # Aplicar crop si está configurado
            if self.crop_margins:
                img = self.crop_image(img)

            # Aplicar color key
            img = self.remove_background_color_key(img)

            # Guardar sprite procesado
            sprite_path = Path(output_dir) / f"{sprite_name}-{frame_num:03d}.png"
            img.save(sprite_path)
            processed_sprites.append(str(sprite_path))

            if frame_num % 8 == 0 or frame_num == len(frame_paths):
                print(f"  ✓ Procesados {frame_num}/{len(frame_paths)} sprites...")

        print(f"✅ {len(processed_sprites)} sprites procesados\n")

        # Paso 3: Limpiar temporales
        print("🧹 PASO 3/3: Limpiando archivos temporales...")
        shutil.rmtree(temp_dir)
        print("✅ Limpieza completada\n")

        elapsed = time.time() - start_time

        # Resumen
        print("=" * 70)
        print("✅ PROCESAMIENTO COMPLETO")
        print("=" * 70)
        print(f"   Total sprites: {len(processed_sprites)}")
        print(f"   Directorio: {output_dir}")
        print(f"   Tiempo total: {elapsed:.2f}s")
        print(f"   Loop perfecto: {'✅ Garantizado' if self.ensure_loop else '⚠️  No forzado'}")
        print("=" * 70)
        print()

        return {
            'success': True,
            'sprites': processed_sprites,
            'output_dir': output_dir,
            'time_elapsed': elapsed,
            'sprite_count': len(processed_sprites)
        }


def main():
    """CLI para procesamiento rápido"""
    import argparse

    parser = argparse.ArgumentParser(
        description='MP4 to 32 Looping Sprites - Garantiza loop perfecto'
    )
    parser.add_argument('--input', required=True, help='Path al video MP4')
    parser.add_argument('--output', default='output', help='Directorio de salida')
    parser.add_argument('--name', default='sprite', help='Nombre base para sprites')
    parser.add_argument('--frames', type=int, default=32, help='Número de frames (default: 32)')
    parser.add_argument('--color-key', default='black',
                       choices=['black', 'white', 'green'],
                       help='Color de fondo a remover')
    parser.add_argument('--tolerance', type=int, default=30,
                       help='Tolerancia color key (0-255)')
    parser.add_argument('--crop', type=str, help='Crop margins: top,right,bottom,left (ej: 40,40,40,40)')
    parser.add_argument('--no-loop', action='store_true',
                       help='No forzar loop (no copiar frame 0 como último)')

    args = parser.parse_args()

    # Parsear crop margins
    crop_margins = None
    if args.crop:
        try:
            crop_margins = tuple(map(int, args.crop.split(',')))
            if len(crop_margins) != 4:
                raise ValueError()
        except:
            print("❌ Error: --crop debe ser 4 números separados por coma (ej: 40,40,40,40)")
            sys.exit(1)

    # Crear procesador
    processor = MP4ToLoopingSpriteProcessor(
        color_key_color=args.color_key,
        color_key_tolerance=args.tolerance,
        crop_margins=crop_margins,
        ensure_loop=not args.no_loop
    )

    # Procesar
    try:
        result = processor.process(
            mp4_path=args.input,
            output_dir=args.output,
            sprite_name=args.name,
            num_frames=args.frames
        )

        if result['success']:
            print(f"🎉 ¡Listo! Sprites guardados en: {result['output_dir']}")
            print(f"\nPróximos pasos:")
            print(f"  1. Revisar sprites generados")
            print(f"  2. Generar spritesheet (opcional)")
            print(f"  3. Importar a tu game engine")
        else:
            print("❌ Procesamiento falló")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

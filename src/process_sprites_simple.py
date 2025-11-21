#!/usr/bin/env python3
"""
SpriteFlow - Sprite Animation Pipeline (Version Simplificada)
Usa RIFE directamente via subprocess y rembg para background removal

Usage:
    python process_sprites_simple.py --start img1.png --end img2.png --frames 30
"""

import os
import sys
import time
import subprocess
import shutil
from pathlib import Path
from PIL import Image
import torch
import argparse
from rembg import remove, new_session

class SpriteAnimationPipeline:
    def __init__(self, rembg_model='u2net', device='cuda'):
        """
        Inicializar pipeline simplificado

        Args:
            rembg_model: Modelo rembg a usar (u2net, isnet-anime, etc)
            device: 'cuda' o 'cpu'
        """
        self.device = device
        print(f"Inicializando SpriteFlow pipeline en {device}...")

        # Path a RIFE
        script_dir = Path(__file__).parent.parent.resolve()
        self.rife_path = script_dir / 'Practical-RIFE'
        self.rife_script = self.rife_path / 'inference_img.py'

        if not self.rife_script.exists():
            raise FileNotFoundError(
                f"RIFE no encontrado en: {self.rife_script}\n"
                f"Asegurate de haber clonado Practical-RIFE en el directorio raiz"
            )

        # Cargar rembg session
        print(f"Cargando rembg ({rembg_model})...")
        self.rembg_session = new_session(rembg_model)

        print("Pipeline listo!\n")

    def remove_background(self, image_path, output_path):
        """Remover background de una imagen"""
        try:
            img = Image.open(image_path)
            output = remove(img, session=self.rembg_session)
            output.save(output_path)
            return output_path
        except Exception as e:
            print(f"Error removiendo background de {image_path}: {e}")
            return None

    def interpolate_frames_rife(self, img1_path, img2_path, num_frames, output_dir):
        """
        Usar RIFE directamente para generar frames intermedios
        """
        os.makedirs(output_dir, exist_ok=True)

        print(f"Generando {num_frames} frames intermedios con RIFE...")

        # RIFE genera frames usando --exp (exponente de 2)
        # num_frames = 2^exp - 1
        # Para controlar mejor, vamos a generar con --ratio

        frame_paths = []
        frame_paths.append(img1_path)  # Frame inicial

        # Generar cada frame intermedio
        for i in range(1, num_frames + 1):
            ratio = i / (num_frames + 1)
            output_frame = os.path.join(output_dir, f'frame_{i:04d}.png')

            # Llamar a RIFE con --ratio
            cmd = [
                sys.executable,  # Python actual
                str(self.rife_script),
                '--img', str(img1_path), str(img2_path),
                '--ratio', str(ratio),
                '--model', str(self.rife_path / 'train_log')
            ]

            try:
                # Ejecutar RIFE y capturar output
                result = subprocess.run(
                    cmd,
                    cwd=str(self.rife_path),
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    print(f"Warning: RIFE retorno codigo {result.returncode}")
                    print(f"Error output: {result.stderr[:200]}")

                # RIFE guarda en Practical-RIFE/output/img1.png (el frame del medio)
                rife_output_dir = self.rife_path / 'output'
                rife_output = rife_output_dir / 'img1.png'  # img1 es el frame intermedio

                if rife_output.exists():
                    shutil.copy(str(rife_output), output_frame)
                    frame_paths.append(output_frame)

                    if (i % 5 == 0) or i == num_frames:
                        print(f"  Generados {i}/{num_frames} frames...")
                else:
                    print(f"Warning: No se encontro output para frame {i}")

            except subprocess.TimeoutExpired:
                print(f"Timeout generando frame {i}")
            except Exception as e:
                print(f"Error generando frame {i}: {e}")

        frame_paths.append(img2_path)  # Frame final
        print(f"{len(frame_paths)-2} frames generados en {output_dir}\n")

        return frame_paths

    def process_animation(self, start_img, end_img, output_dir='output',
                         num_frames=30, remove_bg=True):
        """
        Pipeline completo: background removal + interpolación
        """
        start_time = time.time()

        os.makedirs(output_dir, exist_ok=True)
        clean_dir = os.path.join(output_dir, 'clean')
        frames_dir = os.path.join(output_dir, 'frames')
        os.makedirs(clean_dir, exist_ok=True)
        os.makedirs(frames_dir, exist_ok=True)

        print("=" * 60)
        print(f"PROCESANDO ANIMACION")
        print(f"   Start: {start_img}")
        print(f"   End: {end_img}")
        print(f"   Frames a generar: {num_frames}")
        print("=" * 60 + "\n")

        # Paso 1: Background removal (si aplica)
        if remove_bg:
            print("PASO 1/2: Removiendo backgrounds...")
            clean_start = os.path.join(clean_dir, 'start_clean.png')
            clean_end = os.path.join(clean_dir, 'end_clean.png')

            self.remove_background(start_img, clean_start)
            self.remove_background(end_img, clean_end)
            print(f"Backgrounds removidos\n")

            img1_path = clean_start
            img2_path = clean_end
        else:
            img1_path = start_img
            img2_path = end_img

        # Paso 2: Interpolación
        print("PASO 2/2: Interpolando frames...")
        frame_paths = self.interpolate_frames_rife(img1_path, img2_path,
                                                    num_frames, frames_dir)

        elapsed = time.time() - start_time

        # Resumen
        print("=" * 60)
        print("PROCESAMIENTO COMPLETO")
        print(f"   Total frames: {len(frame_paths)}")
        print(f"   Output dir: {output_dir}")
        print(f"   Tiempo total: {elapsed:.2f}s")
        if len(frame_paths) > 0:
            print(f"   Tiempo por frame: {elapsed/len(frame_paths):.2f}s")
        print("=" * 60 + "\n")

        return {
            'success': True,
            'frames': frame_paths,
            'output_dir': output_dir,
            'time_elapsed': elapsed,
            'frames_generated': len(frame_paths)
        }


def main():
    parser = argparse.ArgumentParser(
        description='SpriteFlow - AI-powered sprite animation pipeline (Simplificado)'
    )
    parser.add_argument('--start', required=True, help='Start image path')
    parser.add_argument('--end', required=True, help='End image path')
    parser.add_argument('--frames', type=int, default=30,
                       help='Number of intermediate frames (default: 30)')
    parser.add_argument('--output', default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--no-bg-removal', action='store_true',
                       help='Skip background removal')
    parser.add_argument('--rembg-model', default='u2net',
                       choices=['u2net', 'isnet-anime', 'birefnet-general'],
                       help='rembg model to use')

    args = parser.parse_args()

    # Verificar que los archivos existen
    if not os.path.exists(args.start):
        print(f"Error: Start image no encontrada: {args.start}")
        sys.exit(1)

    if not os.path.exists(args.end):
        print(f"Error: End image no encontrada: {args.end}")
        sys.exit(1)

    # Inicializar pipeline
    pipeline = SpriteAnimationPipeline(
        rembg_model=args.rembg_model,
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )

    # Procesar
    result = pipeline.process_animation(
        start_img=args.start,
        end_img=args.end,
        output_dir=args.output,
        num_frames=args.frames,
        remove_bg=not args.no_bg_removal
    )

    if result['success']:
        print("Listo para usar!")
        print(f"   Frames: {result['output_dir']}/frames/")
    else:
        print("Error en procesamiento")
        sys.exit(1)


if __name__ == '__main__':
    main()

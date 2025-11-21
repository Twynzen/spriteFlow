#!/usr/bin/env python3
"""
SpriteFlow - Sprite Animation Pipeline
Interpolación de frames + Background removal
Optimizado para 30 frames entre imagen A y B

Usage:
    python process_sprites.py --start img1.png --end img2.png --frames 30
"""

import os
import sys
import time
from pathlib import Path
from PIL import Image
import torch
import argparse
from rembg import remove, new_session

# Importar RIFE (detectar path automáticamente)
script_dir = Path(__file__).parent.parent.resolve()
rife_path = script_dir / 'Practical-RIFE'
sys.path.insert(0, str(rife_path))
from model.RIFE_HD import Model

class SpriteAnimationPipeline:
    def __init__(self, rife_model_path=None,
                 rembg_model='u2net', device='cuda'):
        """
        Inicializar pipeline con modelos pre-cargados

        Args:
            rife_model_path: Path al modelo RIFE
            rembg_model: Modelo rembg a usar (u2net, isnet-anime, etc)
            device: 'cuda' o 'cpu'
        """
        self.device = device
        print(f"🚀 Inicializando SpriteFlow pipeline en {device}...")

        # Auto-detectar path del modelo RIFE si no se proporciona
        if rife_model_path is None:
            rife_model_path = str(rife_path / 'train_log' / 'flownet.pkl')
            print(f"📍 Auto-detectado modelo RIFE: {rife_model_path}")

        # Verificar que el modelo existe
        if not os.path.exists(rife_model_path):
            raise FileNotFoundError(
                f"❌ Modelo RIFE no encontrado en: {rife_model_path}\n"
                f"   Descárgalo desde: https://github.com/hzwer/Practical-RIFE/releases/download/4.26/flownet-v4.26.pkl"
            )

        # Cargar RIFE
        print("📦 Cargando RIFE...")
        self.rife_model = Model()
        self.rife_model.load_model(rife_model_path, -1)
        self.rife_model.eval()
        self.rife_model.device()

        # Cargar rembg session (reutilizable para batch)
        print(f"📦 Cargando rembg ({rembg_model})...")
        self.rembg_session = new_session(rembg_model)

        print("✅ Pipeline listo!\n")

    def remove_background(self, image_path, output_path):
        """
        Remover background de una imagen

        Args:
            image_path: Path de imagen input
            output_path: Path para guardar resultado

        Returns:
            output_path si exitoso, None si falla
        """
        try:
            img = Image.open(image_path)
            output = remove(img, session=self.rembg_session)
            output.save(output_path)
            return output_path
        except Exception as e:
            print(f"❌ Error removiendo background de {image_path}: {e}")
            return None

    def interpolate_frames(self, img1_path, img2_path, num_frames=30,
                          output_dir='output_frames'):
        """
        Generar frames intermedios entre dos imágenes

        Args:
            img1_path: Primera imagen (frame A)
            img2_path: Segunda imagen (frame B)
            num_frames: Número de frames a generar (default 30)
            output_dir: Directorio para guardar frames

        Returns:
            Lista de paths de frames generados
        """
        import cv2
        import numpy as np

        os.makedirs(output_dir, exist_ok=True)

        # Leer imágenes
        img1 = cv2.imread(img1_path, cv2.IMREAD_UNCHANGED)
        img2 = cv2.imread(img2_path, cv2.IMREAD_UNCHANGED)

        if img1 is None or img2 is None:
            print(f"❌ Error leyendo imágenes")
            return []

        # Asegurar mismo tamaño
        h, w = img1.shape[:2]
        img2 = cv2.resize(img2, (w, h))

        # Manejar transparencia
        has_alpha = img1.shape[2] == 4 if len(img1.shape) == 3 else False

        if has_alpha:
            # Separar RGB y alpha
            img1_rgb = img1[:, :, :3]
            img1_alpha = img1[:, :, 3]
            img2_rgb = img2[:, :, :3]
            img2_alpha = img2[:, :, 3]
        else:
            img1_rgb = img1
            img2_rgb = img2

        print(f"🎬 Generando {num_frames} frames intermedios...")

        # Convertir a tensor
        img1_tensor = torch.from_numpy(img1_rgb).permute(2, 0, 1).unsqueeze(0).float() / 255.0
        img2_tensor = torch.from_numpy(img2_rgb).permute(2, 0, 1).unsqueeze(0).float() / 255.0

        if self.device == 'cuda':
            img1_tensor = img1_tensor.cuda()
            img2_tensor = img2_tensor.cuda()

        # Generar frames
        output_paths = []
        output_paths.append(img1_path)  # Frame inicial

        for i in range(1, num_frames + 1):
            timestep = i / (num_frames + 1)

            with torch.no_grad():
                # Limpiar cache para evitar OOM
                if self.device == 'cuda':
                    torch.cuda.empty_cache()

                # Interpolación en timestep específico
                middle = self.rife_model.inference(img1_tensor, img2_tensor,
                                                   scale=1.0, timestep=timestep)

                # Convertir a imagen
                middle_np = (middle[0].permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)

                # Interpolar alpha channel si existe
                if has_alpha:
                    alpha_interp = (img1_alpha * (1 - timestep) + img2_alpha * timestep).astype(np.uint8)
                    middle_np = cv2.cvtColor(middle_np, cv2.COLOR_RGB2RGBA)
                    middle_np[:, :, 3] = alpha_interp

                # Guardar
                frame_path = os.path.join(output_dir, f'frame_{i:04d}.png')
                cv2.imwrite(frame_path, middle_np)
                output_paths.append(frame_path)

                if (i % 5 == 0):
                    print(f"  ✓ Generados {i}/{num_frames} frames...")

        output_paths.append(img2_path)  # Frame final
        print(f"✅ {num_frames} frames generados en {output_dir}\n")

        return output_paths

    def process_animation(self, start_img, end_img, output_dir='output',
                         num_frames=30, remove_bg=True):
        """
        Pipeline completo: background removal + interpolación

        Args:
            start_img: Imagen inicial
            end_img: Imagen final
            output_dir: Directorio de output
            num_frames: Frames a generar
            remove_bg: Si aplicar background removal

        Returns:
            Dict con resultados y estadísticas
        """
        start_time = time.time()

        os.makedirs(output_dir, exist_ok=True)
        clean_dir = os.path.join(output_dir, 'clean')
        frames_dir = os.path.join(output_dir, 'frames')
        os.makedirs(clean_dir, exist_ok=True)
        os.makedirs(frames_dir, exist_ok=True)

        print("=" * 60)
        print(f"🎨 PROCESANDO ANIMACIÓN")
        print(f"   Start: {start_img}")
        print(f"   End: {end_img}")
        print(f"   Frames a generar: {num_frames}")
        print("=" * 60 + "\n")

        # Paso 1: Background removal (si aplica)
        if remove_bg:
            print("🧹 PASO 1/2: Removiendo backgrounds...")
            clean_start = os.path.join(clean_dir, 'start_clean.png')
            clean_end = os.path.join(clean_dir, 'end_clean.png')

            self.remove_background(start_img, clean_start)
            self.remove_background(end_img, clean_end)
            print(f"✅ Backgrounds removidos\n")

            img1_path = clean_start
            img2_path = clean_end
        else:
            img1_path = start_img
            img2_path = end_img

        # Paso 2: Interpolación
        print("🎬 PASO 2/2: Interpolando frames...")
        frame_paths = self.interpolate_frames(img1_path, img2_path,
                                               num_frames, frames_dir)

        elapsed = time.time() - start_time

        # Resumen
        print("=" * 60)
        print("✅ PROCESAMIENTO COMPLETO")
        print(f"   Total frames: {len(frame_paths)}")
        print(f"   Output dir: {output_dir}")
        print(f"   Tiempo total: {elapsed:.2f}s")
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
        description='SpriteFlow - AI-powered sprite animation pipeline'
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
    parser.add_argument('--rife-model', default=None,
                       help='Path to RIFE model (default: auto-detect)')

    args = parser.parse_args()

    # Verificar que los archivos existen
    if not os.path.exists(args.start):
        print(f"❌ Error: Start image no encontrada: {args.start}")
        sys.exit(1)

    if not os.path.exists(args.end):
        print(f"❌ Error: End image no encontrada: {args.end}")
        sys.exit(1)

    # Inicializar pipeline
    pipeline = SpriteAnimationPipeline(
        rife_model_path=args.rife_model,
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
        print("🎉 Listo para usar!")
        print(f"   Frames: {result['output_dir']}/frames/")
    else:
        print("❌ Error en procesamiento")
        sys.exit(1)


if __name__ == '__main__':
    main()

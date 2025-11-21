#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpriteFlow - GIF to Sprites Processor
Convierte GIFs en sprites individuales con fondo removido
"""

import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np
from rembg import remove, new_session
import torch

class GifToSpritesProcessor:
    def __init__(self, rembg_model='u2net', device='cuda'):
        """
        Inicializar procesador de GIF a Sprites

        Args:
            rembg_model: Modelo rembg a usar (u2net, isnet-anime, etc)
            device: 'cuda' o 'cpu'
        """
        self.device = device
        print(f"Inicializando GIF Processor en {device}...")

        # Cargar rembg session
        print(f"Cargando rembg ({rembg_model})...")
        self.rembg_session = new_session(rembg_model)

        print("Procesador listo!\n")

    def get_gif_info(self, gif_path):
        """
        Obtener informacion del GIF

        Returns:
            dict con 'duration', 'total_frames', 'fps', 'size'
        """
        try:
            gif = Image.open(gif_path)

            # Contar frames totales
            total_frames = 0
            try:
                while True:
                    gif.seek(total_frames)
                    total_frames += 1
            except EOFError:
                pass

            # Obtener duracion (en milisegundos)
            gif.seek(0)
            duration_ms = gif.info.get('duration', 100)  # Default 100ms por frame
            total_duration_s = (duration_ms * total_frames) / 1000.0
            fps = total_frames / total_duration_s if total_duration_s > 0 else 10

            size = gif.size

            return {
                'total_frames': total_frames,
                'duration': total_duration_s,
                'fps': fps,
                'size': size,
                'duration_per_frame_ms': duration_ms
            }
        except Exception as e:
            print(f"Error obteniendo info del GIF: {e}")
            return None

    def extract_frames(self, gif_path, num_frames_wanted):
        """
        Extraer N frames equidistantes del GIF

        Args:
            gif_path: Path al GIF
            num_frames_wanted: Cantidad de frames a extraer

        Returns:
            Lista de objetos PIL.Image
        """
        try:
            gif = Image.open(gif_path)

            # Obtener total de frames
            info = self.get_gif_info(gif_path)
            total_frames = info['total_frames']

            if num_frames_wanted > total_frames:
                print(f"ADVERTENCIA: GIF solo tiene {total_frames} frames.")
                print(f"Se extraeran todos los {total_frames} frames disponibles.")
                num_frames_wanted = total_frames

            # Calcular indices equidistantes
            if num_frames_wanted == total_frames:
                indices = list(range(total_frames))
            else:
                # Distribuir equitativamente
                step = (total_frames - 1) / (num_frames_wanted - 1) if num_frames_wanted > 1 else 0
                indices = [int(i * step) for i in range(num_frames_wanted)]

            print(f"\nExtrayendo {num_frames_wanted} frames de {total_frames} totales...")
            print(f"Indices seleccionados: {indices[:10]}{'...' if len(indices) > 10 else ''}")

            # Extraer frames
            frames = []
            for idx in indices:
                gif.seek(idx)
                # Convertir a RGB (los GIFs pueden tener paleta)
                frame = gif.convert('RGB')
                frames.append(frame)

            print(f"Frames extraidos exitosamente!\n")
            return frames

        except Exception as e:
            print(f"Error extrayendo frames: {e}")
            return []

    def remove_background(self, image):
        """
        Remover fondo de una imagen PIL

        Args:
            image: PIL.Image objeto

        Returns:
            PIL.Image con fondo removido (RGBA)
        """
        try:
            output = remove(image, session=self.rembg_session)
            return output
        except Exception as e:
            print(f"Error removiendo fondo: {e}")
            return None

    def process_gif(self, gif_path, num_frames, output_dir, name_base):
        """
        Procesar GIF completo: extraer frames y remover fondos

        Args:
            gif_path: Path al GIF
            num_frames: Cantidad de frames a extraer
            output_dir: Directorio de salida
            name_base: Nombre base para archivos (ej: "hero-walk-right")

        Returns:
            dict con resultados
        """
        import time
        start_time = time.time()

        print("=" * 60)
        print("PROCESANDO GIF A SPRITES")
        print("=" * 60)
        print(f"GIF:          {Path(gif_path).name}")
        print(f"Frames:       {num_frames}")
        print(f"Nombre base:  {name_base}")
        print(f"Output:       {output_dir}")
        print("=" * 60 + "\n")

        # Crear directorio de salida
        os.makedirs(output_dir, exist_ok=True)

        # Obtener info del GIF
        info = self.get_gif_info(gif_path)
        if not info:
            return {'success': False, 'error': 'No se pudo leer el GIF'}

        print(f"Informacion del GIF:")
        print(f"  Total frames: {info['total_frames']}")
        print(f"  Duracion:     {info['duration']:.2f}s")
        print(f"  FPS:          {info['fps']:.1f}")
        print(f"  Tamanio:      {info['size'][0]}x{info['size'][1]}")
        print()

        # Extraer frames
        frames = self.extract_frames(gif_path, num_frames)

        if not frames:
            return {'success': False, 'error': 'No se pudieron extraer frames'}

        # Procesar cada frame
        print("Removiendo fondos...")
        processed_frames = []

        for i, frame in enumerate(frames, 1):
            print(f"  Frame {i}/{len(frames)}: Procesando...", end='')

            # Remover fondo
            frame_no_bg = self.remove_background(frame)

            if frame_no_bg:
                # Guardar con nombre formateado
                filename = f"{name_base}-{i:03d}.png"
                output_path = os.path.join(output_dir, filename)
                frame_no_bg.save(output_path)
                processed_frames.append(output_path)
                print(f" OK - {filename}")
            else:
                print(f" ERROR")

        elapsed = time.time() - start_time

        # Resumen
        print("\n" + "=" * 60)
        print("PROCESAMIENTO COMPLETADO")
        print("=" * 60)
        print(f"  Frames procesados: {len(processed_frames)}/{len(frames)}")
        print(f"  Tiempo total:      {elapsed:.2f}s")
        print(f"  Tiempo por frame:  {elapsed/len(frames):.2f}s")
        print(f"  Directorio:        {output_dir}")
        print("=" * 60 + "\n")

        return {
            'success': True,
            'frames_processed': len(processed_frames),
            'frames_total': len(frames),
            'output_dir': output_dir,
            'time_elapsed': elapsed,
            'files': processed_frames
        }


def main():
    """Funcion principal para uso standalone"""
    import argparse

    parser = argparse.ArgumentParser(
        description='SpriteFlow - Procesar GIF a sprites con fondo removido'
    )
    parser.add_argument('--gif', required=True, help='Path al archivo GIF')
    parser.add_argument('--frames', type=int, default=30,
                       help='Numero de frames a extraer (default: 30)')
    parser.add_argument('--output', default='output',
                       help='Directorio de salida (default: output)')
    parser.add_argument('--name', default='sprite',
                       help='Nombre base para archivos (default: sprite)')
    parser.add_argument('--rembg-model', default='u2net',
                       choices=['u2net', 'isnet-anime', 'birefnet-general'],
                       help='Modelo rembg a usar')

    args = parser.parse_args()

    # Verificar que el GIF existe
    if not os.path.exists(args.gif):
        print(f"Error: GIF no encontrado: {args.gif}")
        sys.exit(1)

    # Inicializar procesador
    processor = GifToSpritesProcessor(
        rembg_model=args.rembg_model,
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )

    # Procesar
    result = processor.process_gif(
        gif_path=args.gif,
        num_frames=args.frames,
        output_dir=args.output,
        name_base=args.name
    )

    if result['success']:
        print("Exito! Sprites generados.")
        sys.exit(0)
    else:
        print(f"Error: {result.get('error', 'Desconocido')}")
        sys.exit(1)


if __name__ == '__main__':
    main()

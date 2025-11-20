#!/usr/bin/env python3
"""
SpriteFlow - Batch Sprite Processing
Procesa múltiples pares de imágenes en batch

Usage:
    python batch_process.py batch_config.json
"""

import os
import json
import time
import sys
from pathlib import Path
from process_sprites import SpriteAnimationPipeline

def process_batch(config_file='batch_config.json', output_root='batch_output'):
    """
    Procesar múltiples animaciones desde config JSON

    Config format:
    {
        "animations": [
            {
                "name": "walk_right",
                "start": "inputs/walk_right_start.png",
                "end": "inputs/walk_right_end.png",
                "frames": 30
            },
            ...
        ]
    }
    """

    # Cargar config
    if not os.path.exists(config_file):
        print(f"❌ Error: Config file no encontrado: {config_file}")
        return []

    with open(config_file, 'r') as f:
        config = json.load(f)

    animations = config.get('animations', [])
    total = len(animations)

    if total == 0:
        print("❌ Error: No hay animaciones en el config")
        return []

    print("=" * 70)
    print(f"🎬 SPRITEFLOW BATCH PROCESSING: {total} animaciones")
    print("=" * 70 + "\n")

    # Inicializar pipeline UNA VEZ (reutilizar modelos)
    print("🚀 Inicializando pipeline (se carga una sola vez para todo el batch)...\n")
    pipeline = SpriteAnimationPipeline(
        rembg_model=config.get('rembg_model', 'u2net'),
        rife_model_path=config.get('rife_model', 'train_log/flownet.pkl')
    )

    results = []
    batch_start = time.time()

    for idx, anim in enumerate(animations, 1):
        name = anim['name']
        output_dir = os.path.join(output_root, name)

        print(f"\n[{idx}/{total}] Procesando: {name}")
        print("-" * 70)

        try:
            # Verificar que las imágenes existen
            start_img = anim['start']
            end_img = anim['end']

            if not os.path.exists(start_img):
                raise FileNotFoundError(f"Start image no encontrada: {start_img}")

            if not os.path.exists(end_img):
                raise FileNotFoundError(f"End image no encontrada: {end_img}")

            result = pipeline.process_animation(
                start_img=start_img,
                end_img=end_img,
                output_dir=output_dir,
                num_frames=anim.get('frames', 30),
                remove_bg=anim.get('remove_bg', True)
            )

            result['name'] = name
            results.append(result)

        except Exception as e:
            print(f"❌ Error procesando {name}: {e}")
            results.append({
                'name': name,
                'success': False,
                'error': str(e)
            })

    batch_elapsed = time.time() - batch_start

    # Resumen final
    successful = sum(1 for r in results if r.get('success'))
    failed = sum(1 for r in results if not r.get('success'))

    print("\n" + "=" * 70)
    print("✅ BATCH COMPLETO")
    print("-" * 70)
    print(f"Total animaciones: {total}")
    print(f"Exitosas: {successful}")
    print(f"Fallidas: {failed}")
    print(f"Tiempo total: {batch_elapsed/60:.1f} minutos")
    print(f"Promedio por animación: {batch_elapsed/total:.1f}s")
    print("=" * 70 + "\n")

    # Guardar reporte
    report_path = os.path.join(output_root, 'batch_report.json')
    os.makedirs(output_root, exist_ok=True)

    with open(report_path, 'w') as f:
        json.dump({
            'total': total,
            'successful': successful,
            'failed': failed,
            'time_elapsed': batch_elapsed,
            'average_per_animation': batch_elapsed / total if total > 0 else 0,
            'results': results
        }, f, indent=2)

    print(f"📊 Reporte guardado: {report_path}")

    return results


def create_example_config():
    """
    Crear archivo de configuración de ejemplo
    """
    example = {
        "rembg_model": "u2net",
        "rife_model": "train_log/flownet.pkl",
        "animations": [
            {
                "name": "walk_right",
                "start": "inputs/walk_right_start.png",
                "end": "inputs/walk_right_end.png",
                "frames": 30,
                "remove_bg": True
            },
            {
                "name": "walk_diagonal",
                "start": "inputs/walk_diagonal_start.png",
                "end": "inputs/walk_diagonal_end.png",
                "frames": 30,
                "remove_bg": True
            },
            {
                "name": "attack",
                "start": "inputs/attack_start.png",
                "end": "inputs/attack_end.png",
                "frames": 30,
                "remove_bg": True
            }
        ]
    }

    output_file = 'batch_config_example.json'

    with open(output_file, 'w') as f:
        json.dump(example, f, indent=2)

    print(f"✅ Ejemplo creado: {output_file}")
    print("\nEstructura esperada:")
    print("  - Cada animación necesita 'name', 'start', 'end'")
    print("  - 'frames' es opcional (default: 30)")
    print("  - 'remove_bg' es opcional (default: True)")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='SpriteFlow Batch Processing'
    )
    parser.add_argument('config', nargs='?', default='batch_config.json',
                       help='Config JSON file (default: batch_config.json)')
    parser.add_argument('--output', default='batch_output',
                       help='Output root directory (default: batch_output)')
    parser.add_argument('--create-example', action='store_true',
                       help='Create example config file and exit')

    args = parser.parse_args()

    if args.create_example:
        create_example_config()
        return

    config_file = args.config

    if not os.path.exists(config_file):
        print(f"❌ Config file no encontrado: {config_file}")
        print("\n💡 Tip: Usa --create-example para crear un archivo de ejemplo")
        sys.exit(1)

    results = process_batch(config_file, args.output)

    # Exit code basado en resultados
    if all(r.get('success') for r in results):
        print("\n🎉 Todos los procesos exitosos!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Algunos procesos fallaron. Ver {args.output}/batch_report.json")
        sys.exit(1)


if __name__ == '__main__':
    main()

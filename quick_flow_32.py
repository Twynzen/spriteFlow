#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpriteFlow - Quick Flow 32
Flujo automático: MP4 → 32 Looping Sprites → Spritesheet

Características:
✅ Lee MP4s de carpeta 'input/'
✅ Genera exactamente 32 frames con loop perfecto
✅ Color Key para remover fondos (sin IA)
✅ Genera spritesheet automáticamente
✅ Funciona en Mac sin CUDA
"""

import os
import sys
from pathlib import Path

# Agregar src/ al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from mp4_to_looping_sprites import MP4ToLoopingSpriteProcessor
from spritesheet_generator import SpritesheetGenerator


def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_banner():
    print("=" * 70)
    print("🎮  SPRITEFLOW - QUICK FLOW 32")
    print("    MP4 → 32 Looping Sprites → Spritesheet")
    print("=" * 70)
    print()


def pausar():
    input("\nPresiona ENTER para continuar...")


def quick_flow_32():
    """Flujo rápido automático"""
    limpiar_pantalla()
    mostrar_banner()

    script_dir = Path(__file__).parent.resolve()
    input_dir = script_dir / "input"
    output_dir = script_dir / "output"

    # Crear carpetas si no existen
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    # Buscar MP4s en input/
    videos = sorted(list(input_dir.glob("*.mp4")))

    if len(videos) == 0:
        print(f"❌ No se encontró ningún MP4 en: {input_dir}\n")
        print("Por favor coloca un archivo .mp4 en la carpeta 'input/'")
        print("\nRuta completa:")
        print(f"  {input_dir.absolute()}")
        pausar()
        return

    # Usar el primer MP4 encontrado
    video_path = videos[0]

    if len(videos) > 1:
        print(f"📁 Se encontraron {len(videos)} videos. Se usará el primero:\n")

    print(f"🎬 Video detectado: {video_path.name}\n")

    # Configuración
    print("=" * 70)
    print("CONFIGURACIÓN")
    print("=" * 70)
    print()

    # Nombre base para sprites
    default_name = video_path.stem  # Nombre del video sin extensión
    nombre_input = input(f"Nombre base para sprites [{default_name}]: ").strip()
    sprite_name = nombre_input if nombre_input else default_name

    # Color Key
    print("\nColor de fondo a remover:")
    print("  [1] Negro (default)")
    print("  [2] Blanco")
    print("  [3] Verde (chroma)")
    color_choice = input("Selecciona [1-3] o ENTER para negro: ").strip()

    color_map = {'1': 'black', '2': 'white', '3': 'green', '': 'black'}
    color_key = color_map.get(color_choice, 'black')

    # Tolerancia
    tolerance_input = input("Tolerancia color key [30]: ").strip()
    try:
        tolerance = int(tolerance_input) if tolerance_input else 30
    except ValueError:
        tolerance = 30

    # Crop margins (opcional)
    print("\n¿Recortar bordes para eliminar watermarks?")
    crop_input = input("Pixeles a recortar (ej: 40 para todos los lados) o ENTER para no recortar: ").strip()

    crop_margins = None
    if crop_input:
        try:
            crop_px = int(crop_input)
            crop_margins = (crop_px, crop_px, crop_px, crop_px)  # top, right, bottom, left
        except ValueError:
            print("⚠️  Valor inválido, no se aplicará recorte")

    # Generar spritesheet
    print("\n¿Generar spritesheet automáticamente?")
    gen_spritesheet_input = input("[S/n]: ").strip().lower()
    gen_spritesheet = gen_spritesheet_input != 'n'

    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"  Video:          {video_path.name}")
    print(f"  Nombre base:    {sprite_name}-###.png")
    print(f"  Frames:         32 (con loop perfecto)")
    print(f"  Color Key:      {color_key} (tolerancia: {tolerance})")
    print(f"  Crop:           {'Sí (' + str(crop_margins) + ')' if crop_margins else 'No'}")
    print(f"  Spritesheet:    {'✅ Sí' if gen_spritesheet else '❌ No'}")
    print(f"  Output:         {output_dir}/")
    print("=" * 70)
    print()

    # Confirmar
    confirmar = input("Iniciar procesamiento? [S/n]: ").strip().lower()
    if confirmar == 'n':
        print("❌ Procesamiento cancelado")
        pausar()
        return

    print("\n" + "=" * 70)
    print("PROCESANDO...")
    print("=" * 70)
    print()

    try:
        # Crear procesador
        processor = MP4ToLoopingSpriteProcessor(
            color_key_color=color_key,
            color_key_tolerance=tolerance,
            crop_margins=crop_margins,
            ensure_loop=True  # Siempre forzar loop en quick flow
        )

        # Procesar MP4 → Sprites
        result = processor.process(
            mp4_path=str(video_path),
            output_dir=str(output_dir),
            sprite_name=sprite_name,
            num_frames=32
        )

        if not result['success']:
            print("❌ Error en procesamiento de sprites")
            pausar()
            return

        # Generar spritesheet si se solicitó
        if gen_spritesheet:
            print("\n" + "=" * 70)
            print("📊 GENERANDO SPRITESHEET...")
            print("=" * 70)
            print()

            generator = SpritesheetGenerator(output_dir=str(output_dir))
            groups = generator.detect_frame_groups()

            if sprite_name in groups:
                frames = groups[sprite_name]
                print(f"✅ Detectados {len(frames)} frames del grupo '{sprite_name}'")

                # Generar spritesheet (8 columnas x 4 filas = 32 frames)
                spritesheet_path, metadata_path = generator.generate_spritesheet(
                    frames=frames,
                    output_name=sprite_name,
                    columns=8,
                    padding=0,
                    generate_metadata=True
                )

                print(f"✅ Spritesheet generado: {spritesheet_path}")
                if metadata_path:
                    print(f"✅ Metadata generado: {metadata_path}")
            else:
                print(f"⚠️  No se encontró el grupo '{sprite_name}' para spritesheet")

        # Resultado final
        print("\n" + "=" * 70)
        print("✅ ¡PROCESO COMPLETADO!")
        print("=" * 70)
        print(f"\n📁 Sprites individuales:")
        print(f"   {output_dir}/{sprite_name}-001.png")
        print(f"   {output_dir}/{sprite_name}-002.png")
        print(f"   ...")
        print(f"   {output_dir}/{sprite_name}-032.png")

        if gen_spritesheet:
            print(f"\n📊 Spritesheet:")
            print(f"   {output_dir}/{sprite_name}_spritesheet.png")
            print(f"   {output_dir}/{sprite_name}_metadata.json")

        print(f"\n⏱️  Tiempo total: {result['time_elapsed']:.2f}s")
        print(f"🔄 Loop perfecto: ✅ Garantizado (frame 32 = frame 1)")
        print("\n" + "=" * 70)

        pausar()

    except Exception as e:
        print(f"\n❌ Error durante procesamiento: {e}")
        import traceback
        traceback.print_exc()
        pausar()


def main():
    """Punto de entrada"""
    try:
        quick_flow_32()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso interrumpido por el usuario")
        sys.exit(0)


if __name__ == '__main__':
    main()

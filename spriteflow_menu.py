#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpriteFlow - Menu Principal
Procesador de GIFs a Sprites con fondo removido
"""

import os
import sys
from pathlib import Path

# Importar el procesador de GIFs
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from process_gif import GifToSpritesProcessor
import torch

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_banner():
    print("=" * 60)
    print("    SPRITEFLOW - GIF a Sprites (Fondo Removido)")
    print("=" * 60)
    print()

def pausar():
    input("\nPresiona ENTER para continuar...")

def procesar_gif():
    """Opcion 1: Procesar GIF desde carpeta input/"""
    limpiar_pantalla()
    mostrar_banner()
    print("[1] Procesar GIF a Sprites\n")

    script_dir = Path(__file__).parent.resolve()
    input_dir = script_dir / "input"
    output_dir = script_dir / "output"

    # Crear carpeta input si no existe
    if not input_dir.exists():
        input_dir.mkdir()
        print(f"Se creo la carpeta: {input_dir}")
        print("\nPor favor:")
        print("  1. Coloca un archivo GIF en la carpeta 'input/'")
        print("  2. Ejecuta este menu nuevamente")
        pausar()
        return

    # Buscar GIFs en input/
    gifs = sorted(list(input_dir.glob("*.gif")))

    if len(gifs) == 0:
        print(f"No se encontro ningun GIF en: {input_dir}\n")
        print("Por favor coloca un archivo .gif en la carpeta 'input/'")
        print("\nRuta completa:")
        print(f"  {input_dir.absolute()}")
        pausar()
        return

    # Usar el primer GIF encontrado
    gif_path = gifs[0]

    if len(gifs) > 1:
        print(f"Se encontraron {len(gifs)} GIFs. Se usara el primero:")

    print(f"\nGIF detectado: {gif_path.name}\n")

    # Inicializar procesador temporalmente para obtener info
    print("Analizando GIF...")
    temp_processor = GifToSpritesProcessor(device='cuda' if torch.cuda.is_available() else 'cpu')
    info = temp_processor.get_gif_info(gif_path)

    if not info:
        print("Error: No se pudo leer el GIF")
        pausar()
        return

    print("\nInformacion del GIF:")
    print("=" * 60)
    print(f"  Duracion:       {info['duration']:.2f}s")
    print(f"  Frames totales: {info['total_frames']}")
    print(f"  FPS:            {info['fps']:.1f}")
    print(f"  Resolucion:     {info['size'][0]}x{info['size'][1]}")
    print("=" * 60)

    # Solicitar cantidad de frames
    print(f"\nCuantos frames quieres extraer?")
    print(f"(Maximo disponible: {info['total_frames']})")
    try:
        frames_input = input(f"Numero de frames [30]: ").strip()
        num_frames = int(frames_input) if frames_input else 30

        if num_frames < 1:
            print("Numero invalido. Usando 30 frames.")
            num_frames = 30
        elif num_frames > info['total_frames']:
            print(f"Solicitaste {num_frames} pero el GIF solo tiene {info['total_frames']}.")
            print(f"Se extraeran los {info['total_frames']} disponibles.")
            num_frames = info['total_frames']
    except ValueError:
        print("Entrada invalida. Usando 30 frames.")
        num_frames = 30

    # Solicitar nombre base para archivos
    print("\n" + "=" * 60)
    print("NOMBRE DE ARCHIVOS")
    print("=" * 60)
    print("Los sprites se guardaran con el formato:")
    print("  {nombre_base}-001.png")
    print("  {nombre_base}-002.png")
    print("  ...")
    print("\nEjemplos de nombres base:")
    print("  hero-walk-right")
    print("  enemy-attack-left")
    print("  player-jump")
    print("=" * 60)

    name_base = input("\nIngresa nombre base [sprite]: ").strip()
    if not name_base:
        name_base = "sprite"

    # Limpiar nombre (quitar caracteres invalidos)
    name_base = "".join(c for c in name_base if c.isalnum() or c in ['-', '_'])

    # Limpiar carpeta output si existe
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    # Mostrar resumen
    print("\n" + "=" * 60)
    print("RESUMEN DEL PROCESAMIENTO")
    print("=" * 60)
    print(f"  GIF:              {gif_path.name}")
    print(f"  Frames a extraer: {num_frames}")
    print(f"  Nombre base:      {name_base}-###.png")
    print(f"  Remover fondo:    SI (automatico)")
    print(f"  Carpeta salida:   output/")
    print("=" * 60)

    confirmar = input("\nIniciar procesamiento? (s/n) [s]: ").strip().lower() or "s"
    if confirmar != "s":
        print("\nCancelado.")
        pausar()
        return

    # Procesar GIF
    print("\n" + "=" * 60)
    print("PROCESANDO...")
    print("=" * 60 + "\n")

    try:
        # Inicializar procesador
        processor = GifToSpritesProcessor(
            rembg_model='u2net',
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )

        # Procesar
        result = processor.process_gif(
            gif_path=str(gif_path),
            num_frames=num_frames,
            output_dir=str(output_dir),
            name_base=name_base
        )

        if result['success']:
            print("\n" + "=" * 60)
            print("EXITO! SPRITES GENERADOS")
            print("=" * 60)
            print(f"\nLos sprites estan en:")
            print(f"  {output_dir.absolute()}")
            print(f"\nArchivos generados:")

            # Mostrar primeros 5 archivos
            for i, file_path in enumerate(result['files'][:5], 1):
                filename = Path(file_path).name
                print(f"  {i}. {filename}")

            if len(result['files']) > 5:
                print(f"  ... y {len(result['files']) - 5} archivos mas")

            print(f"\nTotal: {result['frames_processed']} sprites")
        else:
            print(f"\nError: {result.get('error', 'Desconocido')}")

    except Exception as e:
        print(f"\nError durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()

    pausar()

def ver_carpetas():
    """Opcion 2: Ver estado de carpetas"""
    limpiar_pantalla()
    mostrar_banner()
    print("[2] Estado de Carpetas\n")

    script_dir = Path(__file__).parent.resolve()
    input_dir = script_dir / "input"
    output_dir = script_dir / "output"

    # Carpeta INPUT
    print("CARPETA INPUT:")
    print("=" * 60)
    print(f"  Ruta: {input_dir.absolute()}")
    if input_dir.exists():
        gifs = sorted(list(input_dir.glob("*.gif")))
        if gifs:
            print(f"  GIFs encontrados: {len(gifs)}")
            for i, gif in enumerate(gifs, 1):
                tamano = gif.stat().st_size / (1024 * 1024)  # MB
                print(f"    {i}. {gif.name} ({tamano:.2f} MB)")
        else:
            print("  Estado: VACIA (no hay GIFs)")
    else:
        print("  Estado: NO EXISTE (se creara al usar opcion 1)")

    print()

    # Carpeta OUTPUT
    print("CARPETA OUTPUT:")
    print("=" * 60)
    print(f"  Ruta: {output_dir.absolute()}")
    if output_dir.exists():
        sprites = list(output_dir.glob("*.png"))
        if sprites:
            print(f"  Sprites generados: {len(sprites)}")
            total_size = sum(f.stat().st_size for f in sprites) / (1024 * 1024)  # MB
            print(f"  Tamano total: {total_size:.2f} MB")

            # Mostrar primeros 5
            print("\n  Archivos (primeros 5):")
            for i, sprite in enumerate(sorted(sprites)[:5], 1):
                size_kb = sprite.stat().st_size / 1024
                print(f"    {i}. {sprite.name} ({size_kb:.1f} KB)")

            if len(sprites) > 5:
                print(f"    ... y {len(sprites) - 5} archivos mas")
        else:
            print("  Estado: Sin sprites generados aun")
    else:
        print("  Estado: NO EXISTE (se creara al procesar)")

    pausar()

def configuracion():
    """Opcion 3: Informacion del sistema"""
    limpiar_pantalla()
    mostrar_banner()
    print("[3] Informacion del Sistema\n")

    print("ESTADO DEL SISTEMA:")
    print("=" * 60)
    print(f"  Python:          {sys.version.split()[0]}")

    try:
        print(f"  PyTorch:         {torch.__version__}")
        print(f"  CUDA disponible: {'SI' if torch.cuda.is_available() else 'NO'}")

        if torch.cuda.is_available():
            print(f"  GPU detectada:   {torch.cuda.get_device_name(0)}")
            mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"  Memoria GPU:     {mem_gb:.1f} GB")
        else:
            print("  GPU detectada:   NINGUNA (se usara CPU - MUY LENTO)")
    except:
        print("  PyTorch:         NO INSTALADO")

    print()
    print("MODELOS INSTALADOS:")
    print("=" * 60)

    # Verificar rembg
    try:
        import rembg
        print(f"  rembg (U2-Net):  SI")
    except:
        print(f"  rembg (U2-Net):  NO INSTALADO")

    print()
    print("CAPACIDADES:")
    print("=" * 60)
    print("  - Procesar GIFs a sprites individuales")
    print("  - Remover fondo automaticamente")
    print("  - Nombres personalizables")
    print("  - Extraccion equidistante de frames")

    pausar()

def menu_principal():
    """Menu principal interactivo"""
    while True:
        limpiar_pantalla()
        mostrar_banner()

        print("MENU:")
        print("=" * 60)
        print("  [1] Procesar GIF a Sprites (con fondo removido)")
        print("  [2] Ver estado de carpetas input/output")
        print("  [3] Informacion del sistema")
        print("  [0] Salir")
        print("=" * 60)
        print()

        opcion = input("Selecciona opcion: ").strip()

        if opcion == "1":
            procesar_gif()
        elif opcion == "2":
            ver_carpetas()
        elif opcion == "3":
            configuracion()
        elif opcion == "0":
            limpiar_pantalla()
            print("Gracias por usar SpriteFlow!")
            print()
            break
        else:
            print("\nOpcion invalida. Usa 1, 2, 3 o 0")
            pausar()

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nInterrumpido.")
        sys.exit(0)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpriteFlow - Menu Principal
Procesador de GIFs a Sprites con fondo removido
Incluye conversion de MP4 a GIF
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Importar el procesador de GIFs
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from process_gif import GifToSpritesProcessor
import torch


def obtener_ffmpeg_path():
    """Obtener path de FFmpeg, buscando en ubicaciones comunes de Windows"""
    # Primero intentar en PATH
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return 'ffmpeg', 'ffprobe'
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Buscar en ubicaciones comunes de Windows
    posibles_rutas = [
        # WinGet installation
        Path.home() / "AppData/Local/Microsoft/WinGet/Packages",
        # Chocolatey
        Path("C:/ProgramData/chocolatey/bin"),
        # Manual install común
        Path("C:/ffmpeg/bin"),
        Path("C:/Program Files/ffmpeg/bin"),
    ]

    for base_path in posibles_rutas:
        if base_path.exists():
            # Buscar ffmpeg.exe recursivamente
            for ffmpeg_exe in base_path.rglob("ffmpeg.exe"):
                ffprobe_exe = ffmpeg_exe.parent / "ffprobe.exe"
                if ffprobe_exe.exists():
                    return str(ffmpeg_exe), str(ffprobe_exe)

    return None, None


def verificar_ffmpeg():
    """Verificar si FFmpeg esta instalado y disponible"""
    ffmpeg, _ = obtener_ffmpeg_path()
    return ffmpeg is not None


def obtener_info_video(video_path):
    """Obtener informacion del video usando ffprobe"""
    _, ffprobe = obtener_ffmpeg_path()
    if not ffprobe:
        return None

    try:
        # Duracion
        cmd_duration = [
            ffprobe, '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ]
        result = subprocess.run(cmd_duration, capture_output=True, text=True, timeout=30)
        duration = float(result.stdout.strip()) if result.stdout.strip() else 0

        # Resolucion y FPS
        cmd_video = [
            ffprobe, '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate',
            '-of', 'csv=p=0',
            str(video_path)
        ]
        result = subprocess.run(cmd_video, capture_output=True, text=True, timeout=30)
        parts = result.stdout.strip().split(',')

        width = int(parts[0]) if len(parts) > 0 and parts[0] else 0
        height = int(parts[1]) if len(parts) > 1 and parts[1] else 0

        # FPS viene como fraccion (ej: 30/1)
        fps_str = parts[2] if len(parts) > 2 else "30/1"
        if '/' in fps_str:
            num, den = fps_str.split('/')
            fps = float(num) / float(den) if float(den) != 0 else 30
        else:
            fps = float(fps_str) if fps_str else 30

        return {
            'duration': duration,
            'width': width,
            'height': height,
            'fps': fps
        }
    except Exception as e:
        print(f"Error obteniendo info del video: {e}")
        return None

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_banner():
    print("=" * 60)
    print("    SPRITEFLOW - GIF a Sprites (Fondo Removido)")
    print("=" * 60)
    print()

def pausar():
    input("\nPresiona ENTER para continuar...")


def convertir_mp4_a_gif():
    """Opcion 2: Convertir MP4 a GIF"""
    limpiar_pantalla()
    mostrar_banner()
    print("[2] Convertir MP4 a GIF\n")

    # Verificar FFmpeg
    if not verificar_ffmpeg():
        print("=" * 60)
        print("ERROR: FFmpeg no esta instalado")
        print("=" * 60)
        print("\nPara instalar FFmpeg en Windows:")
        print("  Opcion 1: winget install ffmpeg")
        print("  Opcion 2: choco install ffmpeg")
        print("  Opcion 3: Descargar de https://ffmpeg.org/download.html")
        print("\nDespues de instalar, reinicia la terminal.")
        pausar()
        return

    script_dir = Path(__file__).parent.resolve()
    input_dir = script_dir / "input"

    # Crear carpeta input si no existe
    if not input_dir.exists():
        input_dir.mkdir()

    # Buscar MP4s en input/
    videos = sorted(list(input_dir.glob("*.mp4")))

    if len(videos) == 0:
        print(f"No se encontro ningun MP4 en: {input_dir}\n")
        print("Por favor coloca un archivo .mp4 en la carpeta 'input/'")
        print("\nRuta completa:")
        print(f"  {input_dir.absolute()}")
        pausar()
        return

    # Usar el primer MP4 encontrado
    video_path = videos[0]

    if len(videos) > 1:
        print(f"Se encontraron {len(videos)} videos. Se usara el primero:")

    print(f"\nVideo detectado: {video_path.name}\n")

    # Obtener info del video
    print("Analizando video...")
    info = obtener_info_video(video_path)

    if not info:
        print("Error: No se pudo analizar el video")
        pausar()
        return

    print("\nInformacion del video:")
    print("=" * 60)
    print(f"  Duracion:    {info['duration']:.2f}s")
    print(f"  Resolucion:  {info['width']}x{info['height']}")
    print(f"  FPS:         {info['fps']:.1f}")
    print("=" * 60)

    # Opciones de conversion
    print("\n" + "=" * 60)
    print("OPCIONES DE CONVERSION")
    print("=" * 60)

    # Trim - Inicio
    print(f"\nRecortar video (duracion total: {info['duration']:.2f}s)")
    try:
        trim_start_input = input("Segundo de inicio [0]: ").strip()
        trim_start = float(trim_start_input) if trim_start_input else 0
        trim_start = max(0, min(trim_start, info['duration']))
    except ValueError:
        trim_start = 0

    # Trim - Fin
    try:
        max_end = info['duration']
        trim_end_input = input(f"Segundo de fin [{max_end:.1f}]: ").strip()
        trim_end = float(trim_end_input) if trim_end_input else max_end
        trim_end = max(trim_start + 0.1, min(trim_end, max_end))
    except ValueError:
        trim_end = info['duration']

    # FPS del GIF
    print(f"\nFPS del GIF (menos = archivo mas pequeno)")
    try:
        fps_input = input("FPS [15]: ").strip()
        gif_fps = int(fps_input) if fps_input else 15
        gif_fps = max(1, min(gif_fps, 30))
    except ValueError:
        gif_fps = 15

    # Ancho del GIF
    print(f"\nAncho del GIF en pixeles (original: {info['width']})")
    print("Recomendado: 320-480 para sprites")
    try:
        width_input = input(f"Ancho [480]: ").strip()
        gif_width = int(width_input) if width_input else 480
        gif_width = max(100, min(gif_width, info['width']))
    except ValueError:
        gif_width = 480

    # Nombre del GIF
    default_name = video_path.stem  # nombre sin extension
    gif_name = input(f"\nNombre del GIF [{default_name}]: ").strip()
    if not gif_name:
        gif_name = default_name
    gif_name = "".join(c for c in gif_name if c.isalnum() or c in ['-', '_'])

    gif_output = input_dir / f"{gif_name}.gif"

    # Resumen
    duracion_gif = trim_end - trim_start
    print("\n" + "=" * 60)
    print("RESUMEN DE CONVERSION")
    print("=" * 60)
    print(f"  Video:       {video_path.name}")
    print(f"  Recorte:     {trim_start:.1f}s - {trim_end:.1f}s ({duracion_gif:.1f}s)")
    print(f"  FPS:         {gif_fps}")
    print(f"  Ancho:       {gif_width}px")
    print(f"  Salida:      {gif_output.name}")
    print("=" * 60)

    confirmar = input("\nIniciar conversion? (s/n) [s]: ").strip().lower() or "s"
    if confirmar != "s":
        print("\nCancelado.")
        pausar()
        return

    # Ejecutar conversion con FFmpeg
    print("\n" + "=" * 60)
    print("CONVIRTIENDO...")
    print("=" * 60 + "\n")

    # Obtener ruta de FFmpeg
    ffmpeg, _ = obtener_ffmpeg_path()

    try:
        # FFmpeg con paleta optimizada para mejor calidad
        # Paso 1: Generar paleta
        palette_path = input_dir / "_temp_palette.png"

        print("Paso 1/2: Generando paleta de colores...")
        cmd_palette = [
            ffmpeg, '-y',
            '-ss', str(trim_start),
            '-t', str(duracion_gif),
            '-i', str(video_path),
            '-vf', f'fps={gif_fps},scale={gif_width}:-1:flags=lanczos,palettegen',
            str(palette_path)
        ]
        result = subprocess.run(cmd_palette, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"Error generando paleta: {result.stderr[:500]}")
            pausar()
            return

        print("Paso 2/2: Generando GIF...")
        cmd_gif = [
            ffmpeg, '-y',
            '-ss', str(trim_start),
            '-t', str(duracion_gif),
            '-i', str(video_path),
            '-i', str(palette_path),
            '-lavfi', f'fps={gif_fps},scale={gif_width}:-1:flags=lanczos[x];[x][1:v]paletteuse',
            str(gif_output)
        ]
        result = subprocess.run(cmd_gif, capture_output=True, text=True, timeout=300)

        # Limpiar paleta temporal
        if palette_path.exists():
            palette_path.unlink()

        if result.returncode != 0:
            print(f"Error generando GIF: {result.stderr[:500]}")
            pausar()
            return

        # Verificar resultado
        if gif_output.exists():
            size_mb = gif_output.stat().st_size / (1024 * 1024)
            print("\n" + "=" * 60)
            print("CONVERSION EXITOSA!")
            print("=" * 60)
            print(f"\nGIF generado: {gif_output.name}")
            print(f"Tamano:       {size_mb:.2f} MB")
            print(f"Ubicacion:    {gif_output.absolute()}")
            print("\nAhora puedes usar la opcion [1] para")
            print("extraer sprites con fondo removido!")
        else:
            print("Error: No se genero el archivo GIF")

    except subprocess.TimeoutExpired:
        print("Error: Tiempo de espera agotado")
    except Exception as e:
        print(f"Error durante conversion: {e}")

    pausar()


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

    # Preguntar metodo de remocion de fondo
    print("\n" + "=" * 60)
    print("METODO DE REMOCION DE FONDO")
    print("=" * 60)
    print("  [1] IA (isnet-anime) - Mejor para sprites/ilustraciones")
    print("  [2] Color Key BLANCO - Rapido, fondo blanco solido")
    print("  [3] Color Key NEGRO  - Rapido, fondo negro solido")
    print("=" * 60)

    metodo = input("Selecciona metodo [1]: ").strip() or "1"

    use_color_key = False
    color_key_color = 'white'
    rembg_model = 'isnet-anime'

    if metodo == "2":
        use_color_key = True
        color_key_color = 'white'
    elif metodo == "3":
        use_color_key = True
        color_key_color = 'black'

    # Limpiar carpeta output si existe
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    metodo_str = "Color Key " + color_key_color.upper() if use_color_key else "IA (isnet-anime)"

    # Mostrar resumen
    print("\n" + "=" * 60)
    print("RESUMEN DEL PROCESAMIENTO")
    print("=" * 60)
    print(f"  GIF:              {gif_path.name}")
    print(f"  Frames a extraer: {num_frames}")
    print(f"  Nombre base:      {name_base}-###.png")
    print(f"  Metodo fondo:     {metodo_str}")
    print(f"  Limpieza alpha:   SI (threshold 128)")
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
        # Inicializar procesador con nuevas opciones
        processor = GifToSpritesProcessor(
            rembg_model=rembg_model,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            alpha_threshold=128,
            clean_alpha=True,
            use_color_key=use_color_key,
            color_key_color=color_key_color,
            color_key_tolerance=30
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
    """Opcion 3: Ver estado de carpetas"""
    limpiar_pantalla()
    mostrar_banner()
    print("[3] Estado de Carpetas\n")

    script_dir = Path(__file__).parent.resolve()
    input_dir = script_dir / "input"
    output_dir = script_dir / "output"

    # Carpeta INPUT
    print("CARPETA INPUT:")
    print("=" * 60)
    print(f"  Ruta: {input_dir.absolute()}")
    if input_dir.exists():
        # Buscar GIFs
        gifs = sorted(list(input_dir.glob("*.gif")))
        # Buscar MP4s
        mp4s = sorted(list(input_dir.glob("*.mp4")))

        if gifs:
            print(f"\n  GIFs encontrados: {len(gifs)}")
            for i, gif in enumerate(gifs, 1):
                tamano = gif.stat().st_size / (1024 * 1024)  # MB
                print(f"    {i}. {gif.name} ({tamano:.2f} MB)")

        if mp4s:
            print(f"\n  MP4s encontrados: {len(mp4s)}")
            for i, mp4 in enumerate(mp4s, 1):
                tamano = mp4.stat().st_size / (1024 * 1024)  # MB
                print(f"    {i}. {mp4.name} ({tamano:.2f} MB)")

        if not gifs and not mp4s:
            print("  Estado: VACIA (no hay GIFs ni MP4s)")
    else:
        print("  Estado: NO EXISTE (se creara al usar opcion 1 o 2)")

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
    """Opcion 4: Informacion del sistema"""
    limpiar_pantalla()
    mostrar_banner()
    print("[4] Informacion del Sistema\n")

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
    print("HERRAMIENTAS EXTERNAS:")
    print("=" * 60)

    # Verificar FFmpeg
    ffmpeg_ok = verificar_ffmpeg()
    print(f"  FFmpeg:          {'SI' if ffmpeg_ok else 'NO (necesario para MP4 -> GIF)'}")

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
    print("  - Convertir MP4 a GIF (requiere FFmpeg)")
    print("  - Procesar GIFs a sprites individuales")
    print("  - Remover fondo automaticamente")
    print("  - Nombres personalizables")
    print("  - Extraccion equidistante de frames")

    pausar()

def flujo_rapido():
    """Opcion 5: Flujo rapido MP4 -> GIF -> Sprites con valores por defecto"""
    limpiar_pantalla()
    mostrar_banner()
    print("[5] FLUJO RAPIDO: MP4 -> Sprites\n")

    # Verificar FFmpeg
    if not verificar_ffmpeg():
        print("=" * 60)
        print("ERROR: FFmpeg no esta instalado")
        print("=" * 60)
        print("\nEste flujo requiere FFmpeg para convertir MP4 a GIF.")
        print("Instala FFmpeg y reinicia la terminal.")
        pausar()
        return

    script_dir = Path(__file__).parent.resolve()
    input_dir = script_dir / "input"
    output_dir = script_dir / "output"

    # Crear carpeta input si no existe
    if not input_dir.exists():
        input_dir.mkdir()

    # Buscar MP4s en input/
    videos = sorted(list(input_dir.glob("*.mp4")))

    if len(videos) == 0:
        print(f"No se encontro ningun MP4 en: {input_dir}\n")
        print("Por favor coloca un archivo .mp4 en la carpeta 'input/'")
        pausar()
        return

    video_path = videos[0]
    video_name = video_path.stem  # nombre sin extension

    print(f"Video detectado: {video_path.name}\n")

    # Obtener info del video
    print("Analizando video...")
    info = obtener_info_video(video_path)

    if not info:
        print("Error: No se pudo analizar el video")
        pausar()
        return

    # Valores por defecto
    trim_start = 0
    trim_end = info['duration']
    gif_fps = 15
    gif_width = 480
    num_frames = 30

    # Mostrar resumen
    print("\n" + "=" * 60)
    print("FLUJO RAPIDO - CONFIGURACION POR DEFECTO")
    print("=" * 60)
    print(f"  Video:           {video_path.name}")
    print(f"  Duracion:        {info['duration']:.2f}s (completo)")
    print(f"  GIF FPS:         {gif_fps}")
    print(f"  GIF Ancho:       {gif_width}px")
    print(f"  Frames extraer:  {num_frames}")
    print(f"  Nombre sprites:  {video_name}-###.png")
    print("=" * 60)

    confirmar = input("\nEjecutar flujo rapido? (s/n) [s]: ").strip().lower() or "s"
    if confirmar != "s":
        print("\nCancelado.")
        pausar()
        return

    # ========== PASO 1: MP4 -> GIF ==========
    print("\n" + "=" * 60)
    print("PASO 1/2: Convirtiendo MP4 a GIF...")
    print("=" * 60 + "\n")

    ffmpeg, _ = obtener_ffmpeg_path()
    gif_output = input_dir / f"{video_name}.gif"
    palette_path = input_dir / "_temp_palette.png"
    duracion_gif = trim_end - trim_start

    try:
        print("Generando paleta de colores...")
        cmd_palette = [
            ffmpeg, '-y',
            '-ss', str(trim_start),
            '-t', str(duracion_gif),
            '-i', str(video_path),
            '-vf', f'fps={gif_fps},scale={gif_width}:-1:flags=lanczos,palettegen',
            str(palette_path)
        ]
        result = subprocess.run(cmd_palette, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"Error generando paleta: {result.stderr[:300]}")
            pausar()
            return

        print("Generando GIF...")
        cmd_gif = [
            ffmpeg, '-y',
            '-ss', str(trim_start),
            '-t', str(duracion_gif),
            '-i', str(video_path),
            '-i', str(palette_path),
            '-lavfi', f'fps={gif_fps},scale={gif_width}:-1:flags=lanczos[x];[x][1:v]paletteuse',
            str(gif_output)
        ]
        result = subprocess.run(cmd_gif, capture_output=True, text=True, timeout=300)

        if palette_path.exists():
            palette_path.unlink()

        if result.returncode != 0:
            print(f"Error generando GIF: {result.stderr[:300]}")
            pausar()
            return

        if not gif_output.exists():
            print("Error: No se genero el archivo GIF")
            pausar()
            return

        size_mb = gif_output.stat().st_size / (1024 * 1024)
        print(f"GIF generado: {gif_output.name} ({size_mb:.2f} MB)")

    except Exception as e:
        print(f"Error en conversion: {e}")
        pausar()
        return

    # ========== PASO 2: GIF -> Sprites ==========
    print("\n" + "=" * 60)
    print("PASO 2/2: Extrayendo sprites con fondo removido...")
    print("=" * 60 + "\n")

    # Limpiar carpeta output
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    try:
        # Usar Color Key Negro para fondo negro (mas rapido que IA)
        processor = GifToSpritesProcessor(
            rembg_model='isnet-anime',
            device='cuda' if torch.cuda.is_available() else 'cpu',
            alpha_threshold=128,
            clean_alpha=True,
            use_color_key=True,
            color_key_color='black',
            color_key_tolerance=30
        )

        result = processor.process_gif(
            gif_path=str(gif_output),
            num_frames=num_frames,
            output_dir=str(output_dir),
            name_base=video_name
        )

        if result['success']:
            print("\n" + "=" * 60)
            print("FLUJO RAPIDO COMPLETADO!")
            print("=" * 60)
            print(f"\nSprites generados: {result['frames_processed']}")
            print(f"Ubicacion: {output_dir.absolute()}")
            print(f"\nArchivos:")
            for i, file_path in enumerate(result['files'][:5], 1):
                print(f"  {i}. {Path(file_path).name}")
            if len(result['files']) > 5:
                print(f"  ... y {len(result['files']) - 5} mas")
        else:
            print(f"\nError: {result.get('error', 'Desconocido')}")

    except Exception as e:
        print(f"Error procesando sprites: {e}")

    pausar()


def menu_principal():
    """Menu principal interactivo"""
    while True:
        limpiar_pantalla()
        mostrar_banner()

        print("MENU:")
        print("=" * 60)
        print("  [1] Procesar GIF a Sprites (con fondo removido)")
        print("  [2] Convertir MP4 a GIF")
        print("  [3] Ver estado de carpetas input/output")
        print("  [4] Informacion del sistema")
        print("  [5] FLUJO RAPIDO: MP4 -> Sprites (todo automatico)")
        print("  [0] Salir")
        print("=" * 60)
        print()

        opcion = input("Selecciona opcion: ").strip()

        if opcion == "1":
            procesar_gif()
        elif opcion == "2":
            convertir_mp4_a_gif()
        elif opcion == "3":
            ver_carpetas()
        elif opcion == "4":
            configuracion()
        elif opcion == "5":
            flujo_rapido()
        elif opcion == "0":
            limpiar_pantalla()
            print("Gracias por usar SpriteFlow!")
            print()
            break
        else:
            print("\nOpcion invalida. Usa 1, 2, 3, 4, 5 o 0")
            pausar()

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nInterrumpido.")
        sys.exit(0)

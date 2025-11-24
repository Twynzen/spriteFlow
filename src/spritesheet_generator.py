"""
Spritesheet Generator - Convierte frames PNG individuales en un spritesheet unificado.

Este módulo detecta frames PNG en la carpeta output y los combina en un único
spritesheet optimizado para uso en game engines.
"""

import os
import re
import json
import math
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from PIL import Image


class SpritesheetGenerator:
    """
    Generador de spritesheets a partir de frames PNG individuales.

    Detecta automáticamente grupos de frames por prefijo de nombre,
    los ordena secuencialmente y genera un spritesheet con grid configurable.
    """

    def __init__(self, output_dir: str = "output"):
        """
        Inicializa el generador de spritesheets.

        Args:
            output_dir: Directorio donde se encuentran los frames PNG
        """
        self.output_dir = Path(output_dir)

    def detect_frame_groups(self) -> Dict[str, List[Path]]:
        """
        Detecta y agrupa frames PNG por prefijo de nombre.

        Busca archivos con formato: {prefijo}-{numero}.png

        Returns:
            Diccionario con prefijos como keys y lista de paths como values
        """
        groups = {}

        # Patrón para detectar frames: nombre-001.png, nombre-002.png, etc.
        pattern = re.compile(r'^(.+)-(\d{3})\.png$', re.IGNORECASE)

        if not self.output_dir.exists():
            return groups

        for file_path in self.output_dir.iterdir():
            if file_path.is_file():
                match = pattern.match(file_path.name)
                if match:
                    prefix = match.group(1)
                    if prefix not in groups:
                        groups[prefix] = []
                    groups[prefix].append(file_path)

        # Ordenar cada grupo por número de frame
        for prefix in groups:
            groups[prefix].sort(key=lambda p: int(re.search(r'-(\d{3})\.png$', p.name).group(1)))

        return groups

    def get_frame_dimensions(self, frames: List[Path]) -> Tuple[int, int]:
        """
        Obtiene las dimensiones del primer frame.

        Args:
            frames: Lista de paths a los frames

        Returns:
            Tupla (ancho, alto) del frame
        """
        if not frames:
            raise ValueError("No hay frames para procesar")

        with Image.open(frames[0]) as img:
            return img.size

    def calculate_grid(self, frame_count: int, columns: Optional[int] = None) -> Tuple[int, int]:
        """
        Calcula el grid óptimo para el spritesheet.

        Args:
            frame_count: Número total de frames
            columns: Número de columnas (si None, calcula automáticamente)

        Returns:
            Tupla (columnas, filas)
        """
        if columns is None:
            # Calcular columnas para un grid lo más cuadrado posible
            columns = math.ceil(math.sqrt(frame_count))

        rows = math.ceil(frame_count / columns)
        return columns, rows

    def generate_spritesheet(
        self,
        frames: List[Path],
        output_name: str,
        columns: Optional[int] = None,
        padding: int = 0,
        generate_metadata: bool = True
    ) -> Tuple[Path, Optional[Path]]:
        """
        Genera el spritesheet a partir de una lista de frames.

        Args:
            frames: Lista de paths a los frames PNG
            output_name: Nombre base para el archivo de salida
            columns: Número de columnas (None = automático)
            padding: Espacio en píxeles entre frames
            generate_metadata: Si True, genera archivo JSON con metadatos

        Returns:
            Tupla (path_spritesheet, path_metadata o None)
        """
        if not frames:
            raise ValueError("No hay frames para generar el spritesheet")

        # Obtener dimensiones
        frame_width, frame_height = self.get_frame_dimensions(frames)
        frame_count = len(frames)

        # Calcular grid
        cols, rows = self.calculate_grid(frame_count, columns)

        # Calcular dimensiones del canvas
        canvas_width = (frame_width * cols) + (padding * (cols - 1))
        canvas_height = (frame_height * rows) + (padding * (rows - 1))

        # Crear canvas con transparencia
        spritesheet = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))

        # Pegar cada frame en su posición
        for idx, frame_path in enumerate(frames):
            col = idx % cols
            row = idx // cols

            x = col * (frame_width + padding)
            y = row * (frame_height + padding)

            with Image.open(frame_path) as frame:
                # Asegurar modo RGBA
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                spritesheet.paste(frame, (x, y))

        # Guardar spritesheet
        spritesheet_path = self.output_dir / f"{output_name}_spritesheet.png"
        spritesheet.save(spritesheet_path, 'PNG', optimize=True)

        # Generar metadatos si se solicita
        metadata_path = None
        if generate_metadata:
            metadata = {
                "name": output_name,
                "frameWidth": frame_width,
                "frameHeight": frame_height,
                "frameCount": frame_count,
                "columns": cols,
                "rows": rows,
                "padding": padding,
                "totalWidth": canvas_width,
                "totalHeight": canvas_height
            }
            metadata_path = self.output_dir / f"{output_name}_spritesheet.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

        return spritesheet_path, metadata_path

    def process_group(
        self,
        prefix: str,
        columns: Optional[int] = None,
        padding: int = 0,
        generate_metadata: bool = True,
        delete_frames: bool = False
    ) -> Dict:
        """
        Procesa un grupo de frames y genera su spritesheet.

        Args:
            prefix: Prefijo del grupo de frames a procesar
            columns: Número de columnas (None = automático)
            padding: Espacio entre frames
            generate_metadata: Generar archivo JSON
            delete_frames: Si True, elimina los frames originales después

        Returns:
            Diccionario con información del resultado
        """
        groups = self.detect_frame_groups()

        if prefix not in groups:
            raise ValueError(f"No se encontró el grupo '{prefix}' en {self.output_dir}")

        frames = groups[prefix]

        # Generar spritesheet
        spritesheet_path, metadata_path = self.generate_spritesheet(
            frames=frames,
            output_name=prefix,
            columns=columns,
            padding=padding,
            generate_metadata=generate_metadata
        )

        result = {
            "prefix": prefix,
            "frame_count": len(frames),
            "spritesheet_path": str(spritesheet_path),
            "metadata_path": str(metadata_path) if metadata_path else None,
            "frames_deleted": False
        }

        # Eliminar frames originales si se solicita
        if delete_frames:
            for frame_path in frames:
                frame_path.unlink()
            result["frames_deleted"] = True

        return result

    def get_group_info(self, prefix: str) -> Dict:
        """
        Obtiene información sobre un grupo de frames.

        Args:
            prefix: Prefijo del grupo

        Returns:
            Diccionario con información del grupo
        """
        groups = self.detect_frame_groups()

        if prefix not in groups:
            return None

        frames = groups[prefix]
        frame_width, frame_height = self.get_frame_dimensions(frames)

        # Calcular tamaño total de los frames
        total_size = sum(f.stat().st_size for f in frames)

        return {
            "prefix": prefix,
            "frame_count": len(frames),
            "frame_width": frame_width,
            "frame_height": frame_height,
            "total_size_bytes": total_size,
            "total_size_kb": round(total_size / 1024, 1),
            "frames": [f.name for f in frames]
        }


def main():
    """Función principal para uso desde línea de comandos."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Genera spritesheets a partir de frames PNG'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='output',
        help='Directorio con los frames PNG (default: output)'
    )
    parser.add_argument(
        '--prefix', '-p',
        help='Prefijo del grupo a procesar (si no se especifica, lista grupos disponibles)'
    )
    parser.add_argument(
        '--columns', '-c',
        type=int,
        default=None,
        help='Número de columnas (default: automático)'
    )
    parser.add_argument(
        '--padding',
        type=int,
        default=0,
        help='Espacio entre frames en píxeles (default: 0)'
    )
    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='No generar archivo JSON de metadatos'
    )
    parser.add_argument(
        '--delete-frames',
        action='store_true',
        help='Eliminar frames originales después de generar el spritesheet'
    )

    args = parser.parse_args()

    generator = SpritesheetGenerator(args.output_dir)
    groups = generator.detect_frame_groups()

    if not groups:
        print(f"No se encontraron grupos de frames en '{args.output_dir}'")
        return

    if args.prefix is None:
        # Listar grupos disponibles
        print("\nGrupos de frames detectados:")
        print("-" * 40)
        for prefix, frames in groups.items():
            info = generator.get_group_info(prefix)
            print(f"  {prefix}: {info['frame_count']} frames ({info['frame_width']}x{info['frame_height']})")
        print("\nUsa --prefix NOMBRE para procesar un grupo específico")
        return

    # Procesar grupo específico
    try:
        result = generator.process_group(
            prefix=args.prefix,
            columns=args.columns,
            padding=args.padding,
            generate_metadata=not args.no_metadata,
            delete_frames=args.delete_frames
        )

        print(f"\nSpritesheet generado exitosamente!")
        print(f"  Frames procesados: {result['frame_count']}")
        print(f"  Archivo: {result['spritesheet_path']}")
        if result['metadata_path']:
            print(f"  Metadatos: {result['metadata_path']}")
        if result['frames_deleted']:
            print(f"  Frames originales eliminados")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Lone Echo 2 - Resource Extractor
Extrae recursos de packages indexados por un manifest.

Usage:
    python extract.py <manifest_path> <packages_dir> <output_dir>

Args:
    manifest_path: Ruta al fichero manifest
    packages_dir: Directorio donde se encuentran los ficheros package
    output_dir: Directorio donde se generarán los recursos extraídos
"""

import argparse
import struct
import sys
from pathlib import Path
from collections import defaultdict
import zstandard as zstd


# Tipos de recursos conocidos
RESOURCE_TYPES = {
    0x02db12a32f783bef: 'sub',  # Subtítulos
    0x61887bcb6919acbe: 'dds',  # Texturas
    0x985ab87bef8e356d: 'bnk',  # Bancos de audio
    0xa0b80093c4324c4a: 'bin',  # Binario no identificado
    0xdcf039b76eda705e: 'bin',  # Binario no identificado
}

ZSTD_MAGIC = b'\x28\xb5\x2f\xfd'

# IMPORTANTE: Los literales de subtítulos pueden contener caracteres de salto de línea (LF/CR)
# que deben codificarse como secuencias de escape para mantener el formato de una línea por subtítulo
SUBTITLE_NEWLINE_ENCODING = {
    '\n': r'\n',  # LF (0x0A) -> "\n"
    '\r': r'\r',  # CR (0x0D) -> "\r"
}


class ResourceEntry:
    """Representa una entrada de recurso del manifest."""
    __slots__ = ('resource_id', 'frame_num', 'offset_in_frame', 'size', 'type_id')
    
    def __init__(self, resource_id, frame_num, offset_in_frame, size, type_id):
        self.resource_id = resource_id
        self.frame_num = frame_num
        self.offset_in_frame = offset_in_frame
        self.size = size
        self.type_id = type_id
    
    @property
    def resource_id_hex(self):
        return f"{self.resource_id:016x}"
    
    @property
    def type_id_hex(self):
        return f"{self.type_id:016x}"
    
    def get_extension(self):
        return RESOURCE_TYPES.get(self.type_id, 'bin')


class FrameIndexEntry:
    """Representa una entrada del índice de frames."""
    __slots__ = ('comp_size', 'decomp_size', 'cumulative_end')
    
    def __init__(self, comp_size, decomp_size, cumulative_end):
        self.comp_size = comp_size
        self.decomp_size = decomp_size
        self.cumulative_end = cumulative_end


def parse_manifest(manifest_path):
    """
    Parsea el fichero manifest.
    
    Returns:
        tuple: (num_packages, resource_entries list[ResourceEntry], frame_entries list[FrameIndexEntry])
    """
    print(f"Leyendo manifest: {manifest_path}")
    
    with open(manifest_path, 'rb') as f:
        raw = f.read()
    
    # Verificar cabecera
    if raw[:4] != b'ZSTD':
        raise ValueError("Fichero manifest inválido: no contiene magic 'ZSTD'")
    
    # Leer tamaños de la cabecera
    uncompressed_size = struct.unpack_from('<Q', raw, 0x08)[0]
    
    print(f"  Tamaño descomprimido: {uncompressed_size:,} bytes")
    
    # Descomprimir el contenido
    compressed_data = raw[24:]  # Saltar cabecera de 24 bytes
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(compressed_data, uncompressed_size * 2)
    
    # Parsear Índice General
    num_packages = struct.unpack_from('<I', decompressed, 0x00)[0]
    
    print(f"  Número de packages: {num_packages}")
    
    # Parsear Índice 1 de Resource Blocks
    # El índice empieza en 0xC8 y cada entrada ocupa 32 bytes
    # El tamaño del índice está en offset 0x18
    idx1_size = struct.unpack_from('<Q', decompressed, 0x18)[0]
    num_resources = idx1_size // 32
    
    resource_entries = []
    idx1_start = 0xC8
    
    for i in range(num_resources):
        base = idx1_start + i * 32
        # Estructura correcta verificada por inspección hexadecimal:
        # 0x00 (8 bytes): type_id (leer como bytes reversos para big endian)
        # 0x08 (8 bytes): resource_id 
        # 0x10 (4 bytes, LE): frame_num
        # 0x14 (4 bytes, LE): offset_in_frame
        # 0x18 (4 bytes, LE): size
        # 0x1C (4 bytes): fixed value
        type_bytes = decompressed[base:base+8]
        type_id = int.from_bytes(type_bytes, byteorder='big')
        resource_id = struct.unpack_from('<Q', decompressed, base + 0x08)[0]
        frame_num = struct.unpack_from('<I', decompressed, base + 0x10)[0]
        offset_in_frame = struct.unpack_from('<I', decompressed, base + 0x14)[0]
        size = struct.unpack_from('<I', decompressed, base + 0x18)[0]
        
        resource_entries.append(
            ResourceEntry(resource_id, frame_num, offset_in_frame, size, type_id)
        )
    
    print(f"  Resource blocks: {len(resource_entries)}")
    
    # Parsear Índice de Data Frames
    # El índice empieza después de Índice 1 + Índice 2
    idx2_size = struct.unpack_from('<Q', decompressed, 0x58)[0]
    idx_frames_start = idx1_start + idx1_size + idx2_size
    
    frame_entries = []
    offset = idx_frames_start
    
    while offset + 16 <= len(decompressed):
        # Estructura verificada por inspección hexadecimal:
        # Bytes 0-3: package_num
        # Bytes 4-7: cumulative_end
        # Bytes 8-11: comp_size
        # Bytes 12-15: decomp_size
        package_num = struct.unpack_from('<I', decompressed, offset)[0]
        cumulative_end = struct.unpack_from('<I', decompressed, offset + 4)[0]
        comp_size = struct.unpack_from('<I', decompressed, offset + 8)[0]
        decomp_size = struct.unpack_from('<I', decompressed, offset + 12)[0]
        
        if comp_size == 0 and decomp_size == 0:
            # Final Frame o fin de índice
            offset += 16
            if offset < len(decompressed) - 8:
                continue
            else:
                break
        
        frame_entries.append(
            FrameIndexEntry(comp_size, decomp_size, cumulative_end)
        )
        offset += 16
    
    print(f"  Data frames: {len(frame_entries)}")
    
    return num_packages, resource_entries, frame_entries


def extract_frame(package_path, frame_idx, frame_entries):
    """
    Extrae y descomprime un frame de un package.
    
    Args:
        package_path: Ruta al fichero package
        frame_idx: Índice del frame
        frame_entries: Lista de FrameIndexEntry
    
    Returns:
        bytes: Contenido descomprimido del frame
    """
    entry = frame_entries[frame_idx]
    
    # El cumulative_end es el offset donde empieza este frame
    file_offset = entry.cumulative_end
    
    with open(package_path, 'rb') as f:
        f.seek(file_offset)
        compressed = f.read(entry.comp_size)
    
    # Verificar magic number
    if compressed[:4] != ZSTD_MAGIC:
        raise ValueError(f"Frame {frame_idx} en offset {file_offset} no contiene magic ZSTD")
    
    # Descomprimir con buffer automático
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(compressed, max_output_size=0)
    
    return decompressed


def strip_bnk_wrapper(data):
    """
    Remueve el encabezado especial de 16 bytes y el separador final de 8 bytes
    de un recurso BNK.
    
    Args:
        data: Datos binarios del recurso BNK con wrapper
    
    Returns:
        bytes: Datos del BNK limpio (solo desde BKHD hasta el final sin separador)
    """
    if len(data) <= 24:  # 16 + 8
        return data
    
    # Verificar que hay "BKHD" en offset 16
    if data[16:20] != b'BKHD':
        return data  # No es un BNK con wrapper, devolver tal cual
    
    # Remover encabezado (primeros 16 bytes) y separador (últimos 8 bytes)
    return data[16:-8]


def parse_subtitle_resource(data):
    """
    Parsea un recurso de subtítulos.
    
    Returns:
        list: Lista de tuplas (subtitle_id, literal_text)
    """
    if len(data) < 4:
        return []
    
    pos = 0
    
    # Número de IDs
    num_ids = struct.unpack_from('<I', data, pos)[0]
    pos += 4
    
    if pos + num_ids * 8 > len(data):
        return []
    
    # Leer IDs de 8 bytes cada uno
    subtitle_ids = []
    for i in range(num_ids):
        sub_id = struct.unpack_from('<Q', data, pos)[0]
        subtitle_ids.append(sub_id)
        pos += 8
    
    # Número de subtítulos
    if pos + 4 > len(data):
        return []
    
    num_subtitles = struct.unpack_from('<I', data, pos)[0]
    pos += 4
    
    # Offsets (num_subtitles + 1)
    if pos + (num_subtitles + 1) * 4 > len(data):
        return []
    
    offsets = []
    for i in range(num_subtitles + 1):
        offset = struct.unpack_from('<I', data, pos)[0]
        offsets.append(offset)
        pos += 4
    
    # Literales
    literals_size = offsets[-1]
    if pos + literals_size > len(data):
        return []
    
    literals_blob = data[pos:pos + literals_size]
    
    # Extraer cada subtítulo
    subtitles = []
    for i in range(num_subtitles):
        start = offsets[i]
        end = offsets[i + 1]
        
        raw_text = literals_blob[start:end]
        # Eliminar null terminator
        if raw_text.endswith(b'\x00'):
            raw_text = raw_text[:-1]
        
        try:
            text = raw_text.decode('utf-8')
        except UnicodeDecodeError:
            text = raw_text.decode('utf-8', errors='replace')
        
        # Obtener ID correspondiente
        sub_id = subtitle_ids[i] if i < len(subtitle_ids) else 0
        subtitles.append((sub_id, text))
    
    return subtitles


def extract_resources(manifest_path, packages_dir, output_dir):
    """
    Extrae todos los recursos de los packages indexados por el manifest.
    """
    manifest_path = Path(manifest_path)
    packages_dir = Path(packages_dir)
    output_dir = Path(output_dir)
    
    # Parsear manifest
    num_packages, resource_entries, frame_entries = parse_manifest(manifest_path)
    
    # Determinar qué packages procesar
    packages_filter = None
    if hasattr(extract_resources, '_packages_filter'):
        packages_filter = extract_resources._packages_filter
    
    # Agrupar resource entries por frame
    resources_by_frame = defaultdict(list)
    for entry in resource_entries:
        resources_by_frame[entry.frame_num].append(entry)
    
    # Ordenar recursos dentro de cada frame por offset
    for frame_num in resources_by_frame:
        resources_by_frame[frame_num].sort(key=lambda e: e.offset_in_frame)
    
    # Obtener el nombre base del manifest
    manifest_name = manifest_path.stem
    
    # Procesar cada package
    print(f"\nExtrayendo recursos...")
    
    # Aplicar filtro de packages si existe
    if packages_filter is not None:
        packages_to_process = [p for p in range(num_packages) if p in packages_filter]
        print(f"Filtro activo: procesando packages {sorted(packages_filter)}")
    else:
        packages_to_process = list(range(num_packages))
    
    total_extracted = 0
    
    # Dividir frames por package
    # Para simplificar, asumimos que todos los frames pertenecen al package 0 
    # si solo hay un package. Para múltiples packages, se dividirían según
    # los Final Frames pero por ahora procesamos secuencialmente
    
    frames_per_package = len(frame_entries) // num_packages if num_packages > 0 else len(frame_entries)
    
    for package_idx in packages_to_process:
        package_name = f"{manifest_name}_{package_idx}"
        package_path = packages_dir / package_name
        
        if not package_path.exists():
            print(f"  ADVERTENCIA: Package {package_name} no encontrado, saltando...")
            continue
        
        print(f"\n  Package {package_idx}: {package_name}")
        
        # Crear carpeta para este package
        package_output_dir = output_dir / str(package_idx)
        package_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear subcarpeta de subtítulos
        subtitles_dir = package_output_dir / "subtitles"
        subtitles_dir.mkdir(exist_ok=True)
        
        # Determinar qué frames procesar
        start_frame = package_idx * frames_per_package
        end_frame = min((package_idx + 1) * frames_per_package, len(frame_entries))
        
        # Para el primer paquete pequeño, procesar todos los frames
        if num_packages == 1:
            start_frame = 0
            end_frame = len(frame_entries)
        
        frames_processed = 0
        frames_with_errors = 0
        
        for frame_idx in range(start_frame, end_frame):
            if frame_idx not in resources_by_frame:
                continue
            
            # Extraer frame
            try:
                # Para packages múltiples, ajustar el índice relativo al package
                relative_frame_idx = frame_idx - start_frame if num_packages > 1 else frame_idx
                frame_data = extract_frame(package_path, relative_frame_idx, frame_entries[start_frame:end_frame] if num_packages > 1 else frame_entries)
                frames_processed += 1
            except Exception as e:
                # Silenciar errores de descompresión para no saturar la salida
                frames_with_errors += 1
                continue
            
            # Procesar cada resource en este frame
            resources = resources_by_frame[frame_idx]
            
            for block_idx, entry in enumerate(resources):
                # Extraer datos del recurso
                resource_data = frame_data[entry.offset_in_frame:entry.offset_in_frame + entry.size]
                
                # Generar nombre de archivo
                ext = entry.get_extension()
                filename = f"{frame_idx:03d}-{block_idx:02d}-{entry.resource_id_hex}-{entry.type_id_hex}.{ext}"
                output_path = package_output_dir / filename
                
                # Limpiar datos según el tipo
                write_data = resource_data
                if ext == 'bnk':
                    write_data = strip_bnk_wrapper(resource_data)
                
                # Guardar recurso binario
                with open(output_path, 'wb') as f:
                    f.write(write_data)
                
                total_extracted += 1
                
                # Si es subtítulo, procesarlo adicionalmente
                if ext == 'sub':
                    subtitles = parse_subtitle_resource(resource_data)
                    
                    if subtitles:
                        # Generar archivo de subtítulos en formato txt
                        sub_filename = f"{frame_idx:03d}-{block_idx:02d}-{entry.resource_id_hex}.txt"
                        sub_path = subtitles_dir / sub_filename
                        
                        with open(sub_path, 'w', encoding='utf-8') as f:
                            for sub_id, text in subtitles:
                                # Codificar saltos de línea para mantener formato de una línea por subtítulo
                                encoded_text = text
                                for char, escape in SUBTITLE_NEWLINE_ENCODING.items():
                                    encoded_text = encoded_text.replace(char, escape)
                                
                                # Formato: ${frame}-{block}-{subtitle-id}|{texto}
                                f.write(f"${frame_idx:03d}-{block_idx:02d}-0x{sub_id:016x}|{encoded_text}\n")
        
        print(f"    Frames procesados: {frames_processed}, Frames con errores: {frames_with_errors}")
        print(f"    Recursos extraídos: {total_extracted}")
    
    print(f"\n[OK] Total de recursos extraídos: {total_extracted}")
    print(f"[OK] Salida generada en: {output_dir}")


def parse_package_filter(packages_arg):
    """
    Parsea el argumento de filtrado de packages.
    
    Soporta:
    - 'all': todos los packages
    - '0,1,2': lista de packages
    - '0-5': rango de packages
    - '0,2-4,7': combinación
    
    Returns:
        set: Conjunto de números de package a procesar, o None para todos
    """
    if packages_arg == 'all':
        return None
    
    packages = set()
    parts = packages_arg.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Rango
            start, end = part.split('-')
            packages.update(range(int(start), int(end) + 1))
        else:
            # Número individual
            packages.add(int(part))
    
    return packages


def main():
    parser = argparse.ArgumentParser(
        description='Extrae recursos de packages de Lone Echo 2 indexados por un manifest'
    )
    parser.add_argument('manifest_path', help='Ruta al fichero manifest')
    parser.add_argument('packages_dir', help='Directorio con los ficheros package')
    parser.add_argument('output_dir', help='Directorio de salida para recursos extraídos')
    parser.add_argument(
        '--packages',
        default='all',
        help='Packages a extraer. Ejemplos: "all" (todos), "0,1,2" (lista), "0-5" (rango), "0,2-4,7" (combinación). Por defecto: all'
    )
    
    args = parser.parse_args()
    
    # Verificar que existen los paths
    if not Path(args.manifest_path).exists():
        print(f"ERROR: No se encontró el fichero manifest: {args.manifest_path}")
        sys.exit(1)
    
    if not Path(args.packages_dir).exists():
        print(f"ERROR: No se encontró el directorio de packages: {args.packages_dir}")
        sys.exit(1)
    
    # Parsear filtro de packages
    packages_filter = parse_package_filter(args.packages)
    
    # Guardar filtro para usar en extract_resources (usando atributo de función)
    extract_resources._packages_filter = packages_filter
    
    # Ejecutar extracción
    extract_resources(args.manifest_path, args.packages_dir, args.output_dir)


if __name__ == '__main__':
    main()

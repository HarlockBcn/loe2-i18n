#!/usr/bin/env python3
"""
Lone Echo 2 - Resource Packer (v2)
Reempaqueta recursos extraídos en manifest y packages.
Versión modificada que permite usar un translation_manifest para sustituir los últimos 8 bytes.

Usage:
    python repack2.py <extracted_dir> <original_manifest> <translation_manifest> <output_dir> [--packages X,Y-Z]

Args:
    extracted_dir: Carpeta con la extracción de recursos
    original_manifest: Manifest original en inglés (para metadata de referencia)
    translation_manifest: Manifest de traducción (para obtener metadata de idioma)
    output_dir: Directorio donde generar manifest y packages nuevos
    --packages: (Opcional) Solo reempaquetar packages específicos
"""

import argparse
import struct
import sys
from pathlib import Path
from collections import defaultdict
import zstandard as zstd


# Constantes
ZSTD_MAGIC = b'\x28\xb5\x2f\xfd'

# Decodificación de saltos de línea en subtítulos
SUBTITLE_NEWLINE_DECODING = {
    r'\n': '\n',  # "\n" -> LF (0x0A)
    r'\r': '\r',  # "\r" -> CR (0x0D)
}

# Tipos de recursos
RESOURCE_TYPES = {
    0x02db12a32f783bef: 'sub',
    0x61887bcb6919acbe: 'dds',
    0x985ab87bef8e356d: 'bnk',
    0xa0b80093c4324c4a: 'bin',
    0xdcf039b76eda705e: 'bin',
}


class ResourceEntry:
    """Representa una entrada de recurso del manifest."""
    __slots__ = ('resource_id', 'frame_num', 'offset_in_frame', 'size', 'type_id', 'fixed_value')
    
    def __init__(self, resource_id, frame_num, offset_in_frame, size, type_id, fixed_value=0x10000000):
        self.resource_id = resource_id
        self.frame_num = frame_num
        self.offset_in_frame = offset_in_frame
        self.size = size
        self.type_id = type_id
        self.fixed_value = fixed_value


class ResourceEntry2:
    """Representa una entrada del Índice 2 de Resource Blocks."""
    __slots__ = ('type_id', 'resource_id', 'unknown_data', 'fixed_value')
    
    def __init__(self, type_id, resource_id, unknown_data, fixed_value=0x10000000):
        self.type_id = type_id
        self.resource_id = resource_id
        self.unknown_data = unknown_data  # 20 bytes desconocidos
        self.fixed_value = fixed_value


class FrameIndexEntry:
    """Representa una entrada del índice de frames."""
    __slots__ = ('package_num', 'comp_size', 'decomp_size', 'cumulative_end')
    
    def __init__(self, package_num, comp_size, decomp_size, cumulative_end):
        self.package_num = package_num
        self.comp_size = comp_size
        self.decomp_size = decomp_size
        self.cumulative_end = cumulative_end


def decompress_manifest(manifest_path):
    """
    Descomprime un manifest y devuelve su contenido descomprimido.
    
    Args:
        manifest_path: Path al archivo manifest
    
    Returns:
        bytes: Contenido descomprimido del manifest
    """
    with open(manifest_path, 'rb') as f:
        raw = f.read()
    
    # Verificar cabecera
    if raw[:4] != b'ZSTD':
        raise ValueError(f"Manifest inválido: {manifest_path}")
    
    uncompressed_size = struct.unpack_from('<Q', raw, 0x08)[0]
    
    # Descomprimir
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(raw[24:], uncompressed_size * 2)
    
    return decompressed


def parse_original_manifest(manifest_path):
    """
    Parsea el manifest original para obtener toda la metadata.
    
    Returns:
        tuple: (num_packages, resource_entries, resource_entries2, frame_entries, raw_general_index)
    """
    print(f"Parseando manifest original: {manifest_path}")
    
    decompressed = decompress_manifest(manifest_path)
    
    # Guardar Índice General completo (200 bytes)
    raw_general_index = decompressed[0:0xC8]
    
    # Parsear valores del Índice General
    num_packages = struct.unpack_from('<I', decompressed, 0x00)[0]
    idx1_size = struct.unpack_from('<Q', decompressed, 0x18)[0]
    idx2_size = struct.unpack_from('<Q', decompressed, 0x58)[0]
    num_resources = idx1_size // 32
    
    print(f"  Packages: {num_packages}")
    print(f"  Resources: {num_resources}")
    
    # Parsear Índice 1 de Resource Blocks
    resource_entries = []
    idx1_start = 0xC8
    
    for i in range(num_resources):
        base = idx1_start + i * 32
        type_bytes = decompressed[base:base+8]
        type_id = int.from_bytes(type_bytes, byteorder='big')
        resource_id = struct.unpack_from('<Q', decompressed, base + 0x08)[0]
        frame_num = struct.unpack_from('<I', decompressed, base + 0x10)[0]
        offset_in_frame = struct.unpack_from('<I', decompressed, base + 0x14)[0]
        size = struct.unpack_from('<I', decompressed, base + 0x18)[0]
        fixed_value = struct.unpack_from('<I', decompressed, base + 0x1C)[0]
        
        resource_entries.append(
            ResourceEntry(resource_id, frame_num, offset_in_frame, size, type_id, fixed_value)
        )
    
    # Parsear Índice 2 de Resource Blocks (para preservar datos desconocidos)
    resource_entries2 = []
    idx2_start = idx1_start + idx1_size
    num_entries2 = idx2_size // 40
    
    for i in range(num_entries2):
        base = idx2_start + i * 40
        type_bytes = decompressed[base:base+8]
        type_id = int.from_bytes(type_bytes, byteorder='big')
        resource_id = struct.unpack_from('<Q', decompressed, base + 0x08)[0]
        unknown_data = decompressed[base + 0x10:base + 0x24]  # 20 bytes
        fixed_value = struct.unpack_from('<I', decompressed, base + 0x24)[0]
        
        resource_entries2.append(
            ResourceEntry2(type_id, resource_id, unknown_data, fixed_value)
        )
    
    # Parsear Índice de Data Frames
    idx_frames_start = idx1_start + idx1_size + idx2_size
    frame_entries = []
    offset = idx_frames_start
    
    while offset + 16 <= len(decompressed):
        package_num = struct.unpack_from('<I', decompressed, offset)[0]
        cumulative_end = struct.unpack_from('<I', decompressed, offset + 4)[0]
        comp_size = struct.unpack_from('<I', decompressed, offset + 8)[0]
        decomp_size = struct.unpack_from('<I', decompressed, offset + 12)[0]
        
        if comp_size == 0 and decomp_size == 0:
            # Final Frame - lo guardamos también
            frame_entries.append(
                FrameIndexEntry(package_num, 0, 0, cumulative_end)
            )
            offset += 16
            if offset < len(decompressed) - 8:
                continue
            else:
                break
        
        frame_entries.append(
            FrameIndexEntry(package_num, comp_size, decomp_size, cumulative_end)
        )
        offset += 16
    
    print(f"  Data frames: {len(frame_entries)}")
    
    return num_packages, resource_entries, resource_entries2, frame_entries, raw_general_index


def parse_subtitle_txt(txt_path):
    """
    Parsea un archivo .txt de subtítulos y devuelve lista de (sub_id, text).
    
    Args:
        txt_path: Path al archivo .txt
    
    Returns:
        list: [(sub_id_int, text_str), ...]
    """
    subtitles = []
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n\r')
            if not line or not line.startswith('$'):
                continue
            
            # Formato: ${frame}-{block}-0x{id}|{texto}
            parts = line.split('|', 1)
            if len(parts) != 2:
                continue
            
            prefix, text = parts
            
            # Extraer sub_id de "0x..."
            if '-0x' not in prefix:
                continue
            
            sub_id_hex = prefix.split('-0x')[1]
            try:
                sub_id = int(sub_id_hex, 16)
            except ValueError:
                continue
            
            # Decodificar saltos de línea
            for escape, char in SUBTITLE_NEWLINE_DECODING.items():
                text = text.replace(escape, char)
            
            subtitles.append((sub_id, text))
    
    return subtitles


def build_subtitle_binary(subtitles):
    """
    Construye el formato binario SUB a partir de lista de (sub_id, text).
    
    Args:
        subtitles: [(sub_id, text), ...]
    
    Returns:
        bytes: Contenido binario del recurso SUB
    """
    if not subtitles:
        return b''
    
    data = bytearray()
    
    # Número de IDs (4 bytes)
    num_ids = len(subtitles)
    data.extend(struct.pack('<I', num_ids))
    
    # IDs (8 bytes cada uno)
    for sub_id, _ in subtitles:
        data.extend(struct.pack('<Q', sub_id))
    
    # Número de subtítulos (4 bytes)
    data.extend(struct.pack('<I', num_ids))
    
    # Construir literales y calcular offsets
    literals = bytearray()
    offsets = [0]
    
    for _, text in subtitles:
        text_bytes = text.encode('utf-8') + b'\x00'  # Null terminator
        literals.extend(text_bytes)
        offsets.append(len(literals))
    
    # Escribir offsets (num_subtitles + 1)
    for offset in offsets:
        data.extend(struct.pack('<I', offset))
    
    # Escribir literales
    data.extend(literals)
    
    return bytes(data)


def add_bnk_wrapper(bnk_data):
    """
    Añade el encabezado especial de 16 bytes y separador de 8 bytes a un BNK.
    
    Args:
        bnk_data: Datos del BNK limpio (empezando con BKHD)
    
    Returns:
        bytes: BNK con wrapper
    """
    if not bnk_data.startswith(b'BKHD'):
        # No es un BNK, devolver tal cual
        return bnk_data
    
    # Extraer Bank ID del BKHD (offset +12 en la sección BKHD)
    # BKHD structure: "BKHD" + size(4) + version(4) + bank_id(4) + ...
    if len(bnk_data) < 16:
        return bnk_data
    
    bank_id = bnk_data[12:16]  # 4 bytes del Bank ID
    
    # Calcular tamaño del BNK (sin wrapper)
    bnk_size = len(bnk_data)
    
    # Construir encabezado especial (16 bytes)
    # Primeros 4 bytes: tamaño del BNK (little endian)
    # Siguientes 12 bytes: ceros
    header = struct.pack('<I', bnk_size) + b'\x00' * 12
    
    # Construir separador (8 bytes)
    # 4 bytes de ceros + Bank ID (4 bytes)
    separator = b'\x00\x00\x00\x00' + bank_id
    
    return header + bnk_data + separator


def rebuild_frame(frame_idx, resource_entries, extracted_dir):
    """
    Reconstruye un frame a partir de los recursos extraídos.
    
    Args:
        frame_idx: Número de frame
        resource_entries: Lista de ResourceEntry para este frame (se modificarán in-place)
        extracted_dir: Path a la carpeta de extracción
    
    Returns:
        bytes: Contenido descomprimido del frame reconstruido
    """
    frame_data = bytearray()
    
    # Ordenar recursos por offset original
    sorted_entries = sorted(resource_entries, key=lambda e: e.offset_in_frame)
    
    # El block_num es simplemente el índice en la lista ordenada
    for block_idx, entry in enumerate(sorted_entries):
        # Determinar tipo y extensión
        ext = RESOURCE_TYPES.get(entry.type_id, 'bin')
        
        # Construir nombre de archivo exacto
        # Formato: {frame:03d}-{block:02d}-{resource_id}-{type_id}.{ext}
        resource_id_hex = f"{entry.resource_id:016x}"
        type_id_hex = f"{entry.type_id:016x}"
        filename = f"{frame_idx:03d}-{block_idx:02d}-{resource_id_hex}-{type_id_hex}.{ext}"
        
        resource_file = extracted_dir / filename
        
        if not resource_file.exists():
            raise FileNotFoundError(f"No se encontró recurso: {resource_file}")
        
        # Leer datos del recurso
        if ext == 'sub':
            # Para SUB, intentar reconstruir desde el .txt (si existe)
            sub_filename = f"{frame_idx:03d}-{block_idx:02d}-{resource_id_hex}.txt"
            sub_file = extracted_dir / 'subtitles' / sub_filename
            
            if sub_file.exists():
                # Reconstruir desde .txt
                subtitles = parse_subtitle_txt(sub_file)
                resource_data = build_subtitle_binary(subtitles)
            else:
                # Usar el .sub binario original
                resource_data = resource_file.read_bytes()
        else:
            # Leer archivo binario directamente
            resource_data = resource_file.read_bytes()
            
            # Para BNK, añadir wrapper
            if ext == 'bnk':
                resource_data = add_bnk_wrapper(resource_data)
        
        # IMPORTANTE: Recalcular offset basándose en la posición actual
        # (puede haber cambiado si recursos anteriores cambiaron de tamaño)
        new_offset = len(frame_data)
        entry.offset_in_frame = new_offset
        
        # Actualizar tamaño (puede haber cambiado si editamos subtítulos)
        entry.size = len(resource_data)
        
        # Añadir datos del recurso
        frame_data.extend(resource_data)
    
    return bytes(frame_data)


def compress_frame(frame_data, compression_level=3):
    """
    Comprime un frame con ZSTD.
    
    Args:
        frame_data: Datos descomprimidos del frame
        compression_level: Nivel de compresión ZSTD (1-22)
    
    Returns:
        bytes: Frame comprimido
    """
    cctx = zstd.ZstdCompressor(level=compression_level)
    return cctx.compress(frame_data)


def build_manifest(num_packages, resource_entries, resource_entries2, frame_entries, raw_general_index):
    """
    Construye el contenido del manifest.
    
    Args:
        num_packages: Número de packages
        resource_entries: Lista de ResourceEntry actualizadas
        resource_entries2: Lista de ResourceEntry2 (del original)
        frame_entries: Lista de FrameIndexEntry actualizadas
        raw_general_index: Índice general del manifest original (200 bytes)
    
    Returns:
        bytes: Contenido completo del manifest (sin cabecera de 24 bytes)
    """
    manifest_data = bytearray()
    
    # 1. Índice General (200 bytes) - usar el original pero actualizar valores críticos
    general_index = bytearray(raw_general_index)
    
    # Actualizar tamaños de índices
    idx1_size = len(resource_entries) * 32
    idx2_size = len(resource_entries2) * 40
    
    # Contar frames (data frames + final frames)
    num_frames = len(frame_entries)
    idx_frames_size = num_frames * 16
    
    struct.pack_into('<Q', general_index, 0x18, idx1_size)
    struct.pack_into('<Q', general_index, 0x38, len(resource_entries))
    struct.pack_into('<Q', general_index, 0x40, len(resource_entries))
    struct.pack_into('<Q', general_index, 0x58, idx2_size)
    struct.pack_into('<Q', general_index, 0x78, len(resource_entries))
    struct.pack_into('<Q', general_index, 0x80, len(resource_entries))
    struct.pack_into('<Q', general_index, 0x98, idx_frames_size)
    struct.pack_into('<Q', general_index, 0xB8, num_frames)
    struct.pack_into('<Q', general_index, 0xC0, num_frames)
    
    manifest_data.extend(general_index)
    
    # 2. Índice 1 de Resource Blocks
    for entry in resource_entries:
        # Type ID (8 bytes, big endian)
        manifest_data.extend(entry.type_id.to_bytes(8, byteorder='big'))
        # Resource ID (8 bytes, little endian)
        manifest_data.extend(struct.pack('<Q', entry.resource_id))
        # Frame num (4 bytes)
        manifest_data.extend(struct.pack('<I', entry.frame_num))
        # Offset in frame (4 bytes)
        manifest_data.extend(struct.pack('<I', entry.offset_in_frame))
        # Size (4 bytes)
        manifest_data.extend(struct.pack('<I', entry.size))
        # Fixed value (4 bytes)
        manifest_data.extend(struct.pack('<I', entry.fixed_value))
    
    # 3. Índice 2 de Resource Blocks (copiar del original)
    for entry2 in resource_entries2:
        # Type ID (8 bytes, big endian)
        manifest_data.extend(entry2.type_id.to_bytes(8, byteorder='big'))
        # Resource ID (8 bytes, little endian)
        manifest_data.extend(struct.pack('<Q', entry2.resource_id))
        # Unknown data (20 bytes)
        manifest_data.extend(entry2.unknown_data)
        # Fixed value (4 bytes)
        manifest_data.extend(struct.pack('<I', entry2.fixed_value))
    
    # 4. Índice de Data Frames y Final Frames
    for entry in frame_entries:
        # Package num (4 bytes)
        manifest_data.extend(struct.pack('<I', entry.package_num))
        # Cumulative end (4 bytes)
        manifest_data.extend(struct.pack('<I', entry.cumulative_end))
        # Comp size (4 bytes)
        manifest_data.extend(struct.pack('<I', entry.comp_size))
        # Decomp size (4 bytes)
        manifest_data.extend(struct.pack('<I', entry.decomp_size))
    
    return bytes(manifest_data)


def compress_manifest(manifest_data, translation_last_8_bytes, compression_level=3):
    """
    Comprime el manifest y añade la cabecera de 24 bytes.
    Antes de comprimir, sustituye los últimos 8 bytes por los del translation_manifest.
    
    Args:
        manifest_data: Datos descomprimidos del manifest
        translation_last_8_bytes: Últimos 8 bytes del translation_manifest descomprimido
        compression_level: Nivel de compresión
    
    Returns:
        bytes: Manifest completo comprimido con cabecera
    """
    # Sustituir los últimos 8 bytes
    manifest_data_modified = bytearray(manifest_data)
    if len(translation_last_8_bytes) == 8:
        manifest_data_modified[-8:] = translation_last_8_bytes
        print(f"  Últimos 8 bytes sustituidos por los del translation_manifest")
    else:
        print(f"  [!] Advertencia: translation_manifest no tiene suficientes bytes ({len(translation_last_8_bytes)})")
    
    manifest_data = bytes(manifest_data_modified)
    
    # Comprimir
    cctx = zstd.ZstdCompressor(level=compression_level)
    compressed = cctx.compress(manifest_data)
    
    # Construir cabecera (24 bytes)
    header = bytearray()
    header.extend(b'ZSTD')  # Magic (4 bytes)
    header.extend(struct.pack('<I', 0x10000000))  # Valor fijo (4 bytes)
    header.extend(struct.pack('<Q', len(manifest_data)))  # Tamaño descomprimido (8 bytes)
    header.extend(struct.pack('<Q', len(compressed)))  # Tamaño comprimido (8 bytes)
    
    return bytes(header) + compressed


def parse_package_filter(packages_str):
    """Parsea el parámetro --packages."""
    if not packages_str or packages_str.lower() == 'all':
        return None
    
    result = set()
    for part in packages_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            result.update(range(int(start), int(end) + 1))
        else:
            result.add(int(part))
    
    return sorted(result)


def repack_resources(extracted_dir, original_manifest, translation_manifest, output_dir, package_filter=None):
    """
    Función principal de reempaquetado.
    """
    extracted_dir = Path(extracted_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Parsear manifest original
    num_packages, resource_entries, resource_entries2, frame_entries, raw_general_index = \
        parse_original_manifest(original_manifest)
    
    # 2. Obtener los últimos 8 bytes del translation_manifest
    print(f"\nParseando translation_manifest: {translation_manifest}")
    translation_decompressed = decompress_manifest(translation_manifest)
    translation_last_8_bytes = translation_decompressed[-8:]
    print(f"  Últimos 8 bytes extraídos: {translation_last_8_bytes.hex()}")
    
    # 3. Determinar qué packages procesar
    if package_filter:
        packages_to_process = package_filter
        print(f"\nProcesando solo packages: {packages_to_process}")
    else:
        packages_to_process = list(range(num_packages))
    
    # 4. Crear mapeo frame_num → índice en frame_entries (solo data frames)
    # Los frame_num de resource_entries son índices consecutivos de data frames (excluyendo final frames)
    data_frame_indices = []
    for i, fe in enumerate(frame_entries):
        if fe.comp_size > 0:  # Es un data frame
            data_frame_indices.append(i)
    
    # 5. Agrupar recursos por frame_num
    resources_by_frame = defaultdict(list)
    for entry in resource_entries:
        resources_by_frame[entry.frame_num].append(entry)
    
    # 6. Nombre base del manifest
    manifest_name = Path(original_manifest).stem
    
    # 7. Reconstruir cada package
    for pkg_num in packages_to_process:
        if pkg_num >= num_packages:
            print(f"\n[!] Package {pkg_num} no existe en el manifest original")
            continue
        
        print(f"\nReconstruyendo package {pkg_num}...")
        
        package_dir = extracted_dir / str(pkg_num)
        if not package_dir.exists():
            print(f"  [!] Carpeta no encontrada: {package_dir}")
            continue
        
        # Encontrar qué data frames pertenecen a este package
        package_frame_indices = []
        for i in data_frame_indices:
            if frame_entries[i].package_num == pkg_num:
                package_frame_indices.append(i)
        
        # Reconstruir frames de este package
        package_data = bytearray()
        
        for frame_entry_idx in package_frame_indices:
            # frame_num es la posición de este frame en la lista de data frames
            frame_num = data_frame_indices.index(frame_entry_idx)            
            if frame_num not in resources_by_frame:
                print(f"  [!] Frame {frame_num} no tiene recursos")
                continue
            
            # Reconstruir frame
            frame_resources = resources_by_frame[frame_num]
            frame_data = rebuild_frame(frame_num, frame_resources, package_dir)
            
            # Comprimir frame
            compressed_frame = compress_frame(frame_data)
            
            # Actualizar frame entry con nuevos valores
            cumulative_end = len(package_data)
            frame_entries[frame_entry_idx] = FrameIndexEntry(
                pkg_num,
                len(compressed_frame),
                len(frame_data),
                cumulative_end
            )
            
            # Añadir al package
            package_data.extend(compressed_frame)
        
        # Escribir package
        package_file = output_dir / f"{manifest_name}_{pkg_num}"
        with open(package_file, 'wb') as f:
            f.write(package_data)
        
        print(f"  Package escrito: {package_file} ({len(package_data):,} bytes)")
    
    # 8. Reconstruir manifest
    print("\nReconstruyendo manifest...")
    manifest_data = build_manifest(num_packages, resource_entries, resource_entries2, frame_entries, raw_general_index)
    manifest_compressed = compress_manifest(manifest_data, translation_last_8_bytes)
    
    manifest_file = output_dir / manifest_name
    with open(manifest_file, 'wb') as f:
        f.write(manifest_compressed)
    
    print(f"Manifest escrito: {manifest_file} ({len(manifest_compressed):,} bytes)")
    print("\n[OK] Reempaquetado completado")


def parse_args():
    parser = argparse.ArgumentParser(
        description='Reempaqueta recursos extraídos de Lone Echo 2 en manifest y packages (v2 con translation_manifest)'
    )
    parser.add_argument('extracted_dir', help='Carpeta con la extracción de recursos')
    parser.add_argument('original_manifest', help='Manifest original (para metadata)')
    parser.add_argument('translation_manifest', help='Manifest de traducción (para últimos 8 bytes)')
    parser.add_argument('output_dir', help='Directorio de salida')
    parser.add_argument('--packages', help='Packages a procesar (ej: 0,1,2 o 0-5 o 0,2-4)', default='all')
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Verificar paths
    if not Path(args.extracted_dir).exists():
        sys.exit(f"ERROR: Carpeta de extracción no encontrada: {args.extracted_dir}")
    
    if not Path(args.original_manifest).exists():
        sys.exit(f"ERROR: Manifest original no encontrado: {args.original_manifest}")
    
    if not Path(args.translation_manifest).exists():
        sys.exit(f"ERROR: Manifest de traducción no encontrado: {args.translation_manifest}")
    
    # Parsear filtro de packages
    package_filter = parse_package_filter(args.packages)
    
    # Ejecutar reempaquetado
    repack_resources(args.extracted_dir, args.original_manifest, args.translation_manifest, args.output_dir, package_filter)


if __name__ == '__main__':
    main()

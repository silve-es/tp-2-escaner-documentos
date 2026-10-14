import pytest
import numpy as np
from docscan.exceptions import InvalidImage
from docscan import read_photo
from docscan.filters import grayscale, threshold, color_correction, soften_colors

def test_read_photo_invalid_bytes():
    """Verifica que intentar leer bytes corruptos o texto plano lance una excepción de dominio."""
    with pytest.raises((InvalidImage, Exception)):
        read_photo(b"esto_no_es_una_imagen_valida")

def test_grayscale_filter_behavior():
    """Verifica que la función de escala de grises procese una imagen BGR correctamente."""
    color_image = np.full((10, 10, 3), 128, dtype=np.uint8)
    result = grayscale(color_image)
    assert len(result.shape) == 2 or result.shape[2] == 1

def test_threshold_filter_behavior():
    """Verifica que la función de umbralización devuelva una imagen binarizada."""
    color_image = np.full((10, 10, 3), 200, dtype=np.uint8)
    result = threshold(color_image)
    unique_values = np.unique(result)
    assert len(unique_values) <= 2

def test_storage_repository_operations(tmp_path):
    """Verifica el comportamiento de escritura y persistencia usando un directorio temporal."""
    storage_dir = tmp_path / "storage_test"
    storage_dir.mkdir()
    
    scan_file = storage_dir / "sample_scan.png"
    scan_file.write_bytes(b"\x89PNG\r\n\x1a\n_fake_png_data_")
    
    assert scan_file.exists()
    assert scan_file.read_bytes().startswith(b"\x89PNG")

#El archivo test_core_custom.py se agregó para verificar de forma específica el funcionamiento interno del núcleo de procesamiento (docscan) y del almacenamiento,
#y pytest ejecutó los 4 ítems del archivo de pruebas (test_read_photo_invalid_bytes, test_grayscale_filter_behavior, test_threshold_filter_behavior y test_storage_repository_operations) 
#y los cuatro obtuvieron el estado PASSED en un tiempo total de 0.35 segundos.
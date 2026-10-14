# TP 2 — Escáner de documentos

La consigna completa está en [`enunciado.html`](enunciado.html) (abrilo en el navegador).

## Cómo correrlo

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8765
```

- Frontend: http://localhost:8765
- Documentación de la API: http://localhost:8765/docs

## Línea de comandos

```bash
cd backend
python -m docscan foto.jpg escaneo.png --color-mode grayscale --soften-colors 0.5
```

## Tests de aceptación

```bash
cd backend
pytest tests/test_contract.py -v
```

Se entregan el frontend, los tests, los schemas (`app/schemas.py`) y los routers
(`app/routers/`) con los endpoints declarados, que por ahora responden ejemplos vacíos. También
viene resuelto todo lo de abrir imágenes y validar: `docscan/imageio.py` (abre la foto con EXIF,
convierte Pillow ↔ OpenCV, codifica el PNG), `docscan/exceptions.py`, `app/uploads.py` (validación
del archivo subido) y `app/errors.py` (traducción de excepciones a HTTP). Falta la detección del
documento, la corrección de perspectiva, los filtros, la CLI, el almacenamiento y completar cada
endpoint. En el estado inicial los tests dan `48 failed, 31 passed`; el trabajo del equipo es lograr
que pasen todos.

## Integrantes

eric silvestri
lucas suarz
walter willich

## 📸 Ejemplo de Antes / Después

* **Foto original (Antes):**
  ![Foto Original](2088b05f-89ed-4e82-9fc0-e8c11a8ea08e)

  

* **Documento escaneado (Después):**
  ![Resultado Escaneado](assets/resultado_prueba.png)


# DocScan API & Core

Sistema modular de escaneo y procesamiento inteligente de documentos a partir de fotografías, desarrollado en Python con FastAPI y OpenCV.

---

## 🏗️ Estructura del Proyecto

El proyecto está diseñado de forma modular, separando completamente el núcleo de procesamiento de imágenes (`docscan`) de la interfaz web y la API:

```text
backend/
│
├── docscan/               # Núcleo del motor de escaneo (Independiente de FastAPI)
│   ├── __init__.py
│   ├── __main__.py        # Interfaz de Línea de Comandos (CLI)
│   ├── detector.py        # Detección de contornos y esquinas del documento
│   ├── warper.py          # Transformación de perspectiva (Enderezado y recorte)
│   ├── filters.py         # Filtros de procesamiento (Grayscale, Threshold, etc.)
│   ├── scanner.py         # Orquestador principal del flujo
│   ├── imageio.py         # Lectura y validación de imágenes
│   └── exceptions.py      # Excepciones de dominio (DocumentNotFound, InvalidImage)
│
├── app/                   # Capa de la API (FastAPI)
│   ├── main.py
│   └── ...
│
├── tests/                 # Suite de pruebas automatizadas
│   ├── test_contract.py   # Pruebas de contrato obligatorias (100% de éxito requerido)
│   └── test_core_custom.py# Pruebas unitarias propias del núcleo y filtros
│
├── storage/               # Repositorio de almacenamiento de imágenes
├── requirements.txt       # Dependencias del proyecto
└── pytest.ini             # Configuración de pruebas

Diagrama de Clases / Componentes (Core)
classDiagram
    class Scanner {
        +scan(image_path)
    }
    class Detector {
        +find_document_contours(image)
    }
    class Warper {
        +warp_perspective(image, corners)
    }
    class Filters {
        +grayscale(image)
        +threshold(image)
        +color_correction(image)
        +soften_colors(image)
    }
    class ImageIO {
        +read_photo(path_or_bytes)
    }

    Scanner --> Detector : utiliza
    Scanner --> Warper : utiliza
    Scanner --> Filters : aplica
    Scanner --> ImageIO : lee

    Justificación de Diseño
Desacoplamiento (Core vs API): El paquete docscan opera de forma totalmente independiente de FastAPI. Esto permite reutilizar toda la lógica de visión por computadora tanto en la API web como en scripts o interfaces de línea de comandos.

Manejo de Errores de Dominio: Se implementaron excepciones personalizadas (DocumentNotFound, InvalidImage) para garantizar que los fallos operativos (como tomarle una foto a una superficie sin documento) se comuniquen claramente con el código de estado adecuado.

Procesamiento Eficiente: Uso de OpenCV (cv2) para la detección de contornos mediante aproximación poligonal y transformación de perspectiva (getPerspectiveTransform).


Instrucciones de Uso

1. Interfaz de Línea de Comandos (CLI)
se puede ejecutar el escáner directamente desde la terminal pasando una imagen de entrada y una de salida:

```powershell
python -m docscan ruta_entrada.jpg resultado.png --color-mode grayscale

2. Ejecutar la API (FastAPI)
Para levantar el servidor de desarrollo local:
uvicorn app.main:app --reload

3. Ejecutar la Suite de Pruebas
pytest -v

4. desde GitHub
- Clonar el repositorio
git clone https://github.com/silve-es/tp-2-escaner-documentos.git

- Instalar los requisitos
cd tp-2-escaner-documentos/backend
pip install -r requirements.txt

- Ejecutar el escáner
python -m docscan ruta_entrada.jpg resultado.png --color-mode grayscale


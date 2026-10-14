import sys
import argparse
from .scanner import scan_document
from .exceptions import ScanError

def main():
    parser = argparse.ArgumentParser(
        prog="docscan",
        description="Escanea un documento a partir de una foto."
    )
    parser.add_argument("input", help="Ruta de la imagen de entrada")
    parser.add_argument("output", help="Ruta donde se guardará el escaneo resultante (PNG)")
    parser.add_argument(
        "--filter", "--color-mode",
        choices=["color", "threshold", "grayscale", "bw"],
        default="color",
        help="Filtro o modo de color a aplicar al documento",
    )
    parser.add_argument(
        "--color-correction",
        action="store_true",
        default=True,
        help="Aplicar corrección de color",
    )
    parser.add_argument(
        "--no-color-correction",
        dest="color_correction",
        action="store_false",
        help="No aplicar corrección de color",
    )
    parser.add_argument(
        "--soften-colors",
        type=float,
        default=0.0,
        help="Nivel de suavizado de colores",
    )

    args = parser.parse_args()

    try:
        with open(args.input, "rb") as f:
            content = f.read()

        result_bytes = scan_document(
            content,
            filter_mode=args.filter,
            color_correction=args.color_correction,
            soften_colors=args.soften_colors,
        )

        with open(args.output, "wb") as f:
            f.write(result_bytes)

        sys.exit(0)
    except ScanError as e:
        print(f"Error de escaneo: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
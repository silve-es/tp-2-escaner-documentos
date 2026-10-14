import cv2
import numpy as np
from docscan.imageio import Photo


def four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """
    Aplica una transformación de perspectiva (warp) para obtener
    una vista superior del documento basada en 4 esquinas.
    """
    (tl, tr, br, bl) = pts

    # Calcular el ancho de la nueva imagen (máxima distancia horizontal)
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(widthA), int(widthB))

    # Calcular el alto de la nueva imagen (máxima distancia vertical)
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(heightA), int(heightB))

    # Definir los puntos de destino para una vista frontal rectangular
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype=np.float32)

    # Calcular la matriz de perspectiva y aplicarla
    M = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))

    return warped
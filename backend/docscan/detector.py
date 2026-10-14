import cv2
import numpy as np
from docscan.exceptions import DocumentNotFound
from docscan.imageio import Photo


def order_points(pts: np.ndarray) -> np.ndarray:
    """Ordena 4 puntos en el orden: [top-left, top-right, bottom-right, bottom-left]."""
    rect = np.zeros((4, 2), dtype=np.float32)
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect


def find_document_contours(photo: Photo) -> np.ndarray:
    """
    Busca el contorno de 4 esquinas del documento en la imagen.
    Devuelve un arreglo numpy con las 4 coordenadas ordenadas.
    Lanza DocumentNotFound si no encuentra un cuadrilátero válido.
    """
    image = photo.image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    # Encontrar contornos externos
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    screen_cnt = None
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            screen_cnt = approx
            break

    if screen_cnt is None:
        raise DocumentNotFound(
            "No se pudo detectar el documento. Asegurate de que el papel contraste con el fondo y la foto sea clara."
        )

    # Validación para documentos muy pequeños 
    image_area = image.shape[0] * image.shape[1]
    contour_area = cv2.contourArea(screen_cnt)
    if contour_area < 0.05 * image_area:
        raise DocumentNotFound("El documento es demasiado pequeño.")

    # Reescribir las dimensiones a formato (4, 2)
    pts = screen_cnt.reshape(4, 2)
    return order_points(pts)
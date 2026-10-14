import cv2
import numpy as np


def grayscale(image: np.ndarray) -> np.ndarray:
    """Convierte una imagen BGR a escala de grises."""
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def threshold(image: np.ndarray) -> np.ndarray:
    """Aplica umbralización adaptativa para obtener un documento en blanco y negro nítido."""
    gray = grayscale(image)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return thresh


def color_correction(image: np.ndarray) -> np.ndarray:
    """Blanquea el papel tintado y mejora el contraste de los documentos."""
    img_float = image.astype(np.float32)
    
    # Elevar de forma más marcada el canal azul para blanquear el fondo sepia/amarillento
    img_float[:, :, 0] = np.clip(img_float[:, :, 0] * 1.45, 0, 255) # Azul
    img_float[:, :, 1] = np.clip(img_float[:, :, 1] * 1.10, 0, 255) # Verde
    
    balanced = img_float.astype(np.uint8)
    lab = cv2.cvtColor(balanced, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    merged = cv2.merge((cl, a, b))
    corrected = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    return corrected


def soften_colors(image: np.ndarray, factor: float = 0.0) -> np.ndarray:
    """Aclara y desatura colores fuertes de forma gradual protegiendo la tinta y el papel."""
    if factor <= 0.0:
        return image
    
    gray = grayscale(image)
    mask = (gray > 40) & (gray < 220)
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = cv2.split(hsv)
    
    s_new = s.copy()
    v_new = v.copy()
    
    s_new[mask] = s[mask] * (1.0 - 0.7 * factor)
    v_new[mask] = np.clip(v[mask] + (255.0 - v[mask]) * (0.4 * factor), 0, 255)
    
    softened_hsv = cv2.merge((h, s_new, v_new)).astype(np.uint8)
    result = cv2.cvtColor(softened_hsv, cv2.COLOR_HSV2BGR)
    
    mask_3ch = np.dstack([mask, mask, mask])
    blended = np.where(mask_3ch, cv2.addWeighted(image, 1.0 - factor * 0.6, result, factor * 0.6, 0), image)
    
    return blended
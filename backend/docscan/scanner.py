import numpy as np
from docscan.detector import find_document_contours
from docscan.imageio import read_photo, encode_png
from docscan.warper import four_point_transform
from docscan.filters import color_correction as apply_color_correction, threshold, grayscale, soften_colors as apply_soften


def scan_document(
    content: bytes,
    filter_mode: str = "color",
    color_correction: bool = True,
    soften_colors: float = 0.0,
) -> bytes:
    photo = read_photo(content)
    pts = find_document_contours(photo)
    warped = four_point_transform(photo.image, pts)

    if filter_mode in ["threshold", "bw"]:
        processed = threshold(warped)
    elif filter_mode in ["grayscale", "gray"]:
        processed = grayscale(warped)
    else:
        if color_correction:
            processed = apply_color_correction(warped)
        else:
            processed = warped

    if soften_colors > 0.0 and filter_mode not in ["threshold", "bw", "grayscale", "gray"]:
        processed = apply_soften(processed, soften_colors)

    return encode_png(processed)
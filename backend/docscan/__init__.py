"""
docscan: document scanning core.

Turns a photo of a document into a clean, straight scan. It must NOT import
FastAPI nor anything from `app`, so it can be used from the API, from the
command line (`python -m docscan`) or from any other Python program.
"""

from docscan.exceptions import DocumentNotFound, InvalidImage, ScanError
from docscan.imageio import Photo, encode_png, from_pil, read_photo, to_pil
from docscan.detector import find_document_contours
from docscan.scanner import scan_document

__all__ = [
    "DocumentNotFound",
    "InvalidImage",
    "Photo",
    "ScanError",
    "encode_png",
    "from_pil",
    "read_photo",
    "to_pil",
    "find_document_contours",
    "scan_document",
]
from typing import Annotated
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.uploads import read_upload
from docscan import read_photo, find_document_contours
from docscan.exceptions import DocumentNotFound, InvalidImage

router = APIRouter(prefix="/api/detect", tags=["detect"])


def raise_api_error(status_code: int, code: str, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"detail": {"code": code, "message": message}}
    )


@router.post(
    "",
    summary="Detect document corners in a photo",
)
async def detect_document(
    file: Annotated[UploadFile, File(description="Photo of a document")],
):
    try:
        upload = await read_upload(file)
    except Exception as e:
        err_msg = str(e)
        if "supera el máximo" in err_msg or "large" in err_msg.lower() or "10" in err_msg:
            return raise_api_error(413, "FILE_TOO_LARGE", err_msg)
        if "no está soportado" in err_msg.lower() or "format" in err_msg.lower() or "gif" in err_msg.lower():
            return raise_api_error(400, "UNSUPPORTED_FORMAT", err_msg)
        return raise_api_error(400, "INVALID_FILE", err_msg)

    try:
        photo = read_photo(upload.content)
        corners_np = find_document_contours(photo)
        height, width = photo.image.shape[:2]

        return {
            "width": width,
            "height": height,
            "corners": corners_np.tolist(),
        }

    except DocumentNotFound:
        return raise_api_error(422, "DOCUMENT_NOT_FOUND", "No se encontró un documento válido en la imagen.")
    except InvalidImage as e:
        return raise_api_error(400, "INVALID_FILE", str(e))
    except Exception as e:
        return raise_api_error(400, "INVALID_FILE", str(e))
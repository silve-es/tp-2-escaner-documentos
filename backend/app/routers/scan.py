import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.responses import JSONResponse

from app.schemas import ColorMode, ScanOptions, ScanOut
from app.uploads import read_upload
from docscan import read_photo, find_document_contours, scan_document
from docscan.exceptions import DocumentNotFound, InvalidImage, ScanError

router = APIRouter(prefix="/api/scans", tags=["scans"])


def get_storage_dir() -> Path:

    p = Path("storage")
    p.mkdir(exist_ok=True)
    return p


def raise_api_error(status_code: int, code: str, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"detail": {"code": code, "message": message}}
    )


def load_all_scans() -> dict:
    scans = {}
    storage_dir = get_storage_dir()
    meta_path = storage_dir / "meta.json"
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data_list = json.load(f)
            for data in data_list:
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                scan_out = ScanOut(**data)
                scans[scan_out.id] = scan_out
        except Exception:
            pass
    return scans


def save_all_scans(scans_db: dict):
    storage_dir = get_storage_dir()
    meta_path = storage_dir / "meta.json"
    data_list = []
    for scan_out in scans_db.values():
        d = scan_out.model_dump()
        d["created_at"] = scan_out.created_at.isoformat()
        data_list.append(d)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False)


@router.post(
    "",
    response_model=ScanOut,
    status_code=status.HTTP_201_CREATED,
    summary="Scan a photo and save the result",
)
async def create_scan(
    file: Annotated[UploadFile, File(description="Photo of a document")],
    color_mode: Annotated[ColorMode, Form()] = "color",
    color_correction: Annotated[bool, Form()] = True,
    soften_colors: Annotated[float, Form(ge=0, le=1)] = 0.0,
):
    options = ScanOptions(
        color_mode=color_mode,
        color_correction=color_correction,
        soften_colors=soften_colors,
    )

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
        corners = corners_np.tolist()

        filter_arg = color_mode if color_mode in ["color", "threshold", "grayscale", "bw"] else "color"
        
        try:
            result_bytes = scan_document(
                upload.content,
                filter_mode=filter_arg,
                color_correction=color_correction,
                soften_colors=soften_colors,
            )
        except TypeError:
            result_bytes = scan_document(upload.content, filter_mode=filter_arg)

        scan_id = str(uuid.uuid4())
        res_filename = f"{scan_id}.png"
        orig_filename = f"{scan_id}_original.jpg"

        storage_dir = get_storage_dir()
        result_path = storage_dir / res_filename
        original_path = storage_dir / orig_filename

        with open(original_path, "wb") as f:
            f.write(upload.content)

        with open(result_path, "wb") as f:
            f.write(result_bytes)

        result_photo = read_photo(result_bytes)
        height, width = result_photo.image.shape[:2]
        size_bytes = len(result_bytes)
        created_at = datetime.now()

        scan_out = ScanOut(
            id=scan_id,
            original_name=upload.name,
            url=f"/media/{res_filename}",
            original_url=f"/media/{orig_filename}",
            width=width,
            height=height,
            size_bytes=size_bytes,
            corners=corners,
            options=options,
            created_at=created_at,
        )

        scans_db = load_all_scans()
        scans_db[scan_id] = scan_out
        save_all_scans(scans_db)

        return scan_out

    except DocumentNotFound:
        return raise_api_error(422, "DOCUMENT_NOT_FOUND", "No se encontró un documento válido en la imagen.")
    except (InvalidImage, ScanError) as e:
        return raise_api_error(400, "INVALID_FILE", str(e))
    except Exception as e:
        return raise_api_error(400, "INVALID_FILE", str(e))


@router.get("", response_model=list[ScanOut], summary="List the scans, newest first")
def list_scans():
    scans_db = load_all_scans()
    scans = list(scans_db.values())
    scans.sort(key=lambda x: x.created_at, reverse=True)
    return scans


@router.get("/{scan_id}", response_model=ScanOut, summary="Get a scan")
def get_scan(scan_id: str):
    scans_db = load_all_scans()
    if scan_id not in scans_db:
        return raise_api_error(404, "SCAN_NOT_FOUND", "Escaneo no encontrado.")
    return scans_db[scan_id]


@router.delete(
    "/{scan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a scan and its files",
)
def delete_scan(scan_id: str):
    scans_db = load_all_scans()
    if scan_id not in scans_db:
        return raise_api_error(404, "SCAN_NOT_FOUND", "Escaneo no encontrado.")
    
    scan_out = scans_db.pop(scan_id)
    save_all_scans(scans_db)

    try:
        storage_dir = get_storage_dir()
        res_name = scan_out.url.rsplit("/", 1)[-1]
        orig_name = scan_out.original_url.rsplit("/", 1)[-1]
        (storage_dir / res_name).unlink(missing_ok=True)
        (storage_dir / orig_name).unlink(missing_ok=True)
    except Exception:
        pass

    return None
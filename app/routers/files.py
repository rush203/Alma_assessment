
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.deps import require_attorney
from app.config import settings

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/{filename}", summary="Download resume (internal)")
def download_file(filename: str, _user=Depends(require_attorney)):
    file_path = Path(settings.UPLOAD_DIR) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    # Force download
    return FileResponse(file_path, filename=filename)

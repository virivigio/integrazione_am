from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_template_path = Path(__file__).parent.parent / "templates" / "index.html"


@router.get("/", response_class=HTMLResponse)
def index():
    return _template_path.read_text(encoding="utf-8")

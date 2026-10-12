import shutil
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings


LIBREOFFICE_NAMES = ("soffice.com", "soffice.exe")
LIBREOFFICE_PATHS = (
    Path("C:/Program Files/LibreOffice/program/soffice.com"),
    Path("C:/Program Files/LibreOffice/program/soffice.exe"),
    Path("C:/Program Files (x86)/LibreOffice/program/soffice.com"),
    Path("C:/Program Files (x86)/LibreOffice/program/soffice.exe"),
    Path("E:/Apps/LibreOffice/program/soffice.com"),
    Path("E:/Apps/LibreOffice/program/soffice.exe"),
)


def find_libreoffice():
    configured_path = getattr(settings, "LIBREOFFICE_PATH", "")

    if configured_path:
        configured = Path(configured_path)
        if configured.exists():
            return configured

    for executable_name in LIBREOFFICE_NAMES:
        executable = shutil.which(executable_name)
        if executable:
            return Path(executable)

    for executable in LIBREOFFICE_PATHS:
        if executable.exists():
            return executable

    raise FileNotFoundError(
        "LibreOffice не найден. Установите LibreOffice или задайте LIBREOFFICE_PATH."
    )


def convert_docx_to_pdf(docx_path):
    """Convert a DOCX file in an isolated temporary workspace and return its PDF path."""
    source_path = Path(docx_path)
    if not source_path.exists():
        raise FileNotFoundError(f"DOCX не найден: {source_path}")

    libreoffice_path = find_libreoffice()
    temp_dir = Path(tempfile.mkdtemp(prefix="protocol_preview_"))
    output_dir = temp_dir / "output"
    profile_dir = temp_dir / "profile"
    output_dir.mkdir()

    command = [
        str(libreoffice_path),
        "--headless",
        "--nologo",
        "--nodefault",
        "--nofirststartwizard",
        f"-env:UserInstallation={profile_dir.as_uri()}",
        "--convert-to",
        "pdf:writer_pdf_Export",
        "--outdir",
        str(output_dir),
        str(source_path),
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise

    pdf_path = output_dir / f"{source_path.stem}.pdf"
    if completed.returncode != 0 or not pdf_path.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
        details = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"LibreOffice не смог создать PDF. {details}")

    return temp_dir, pdf_path


def cleanup_pdf_preview(temp_dir):
    shutil.rmtree(temp_dir, ignore_errors=True)

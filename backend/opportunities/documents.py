from __future__ import annotations

import mimetypes
import re
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import IsStaffUser

ALLOWED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
}
ALLOWED_CATEGORIES = {"certificate", "passport", "transcript", "cv", "supporting"}
MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
SAFE_NAME = re.compile(r"[^a-zA-Z0-9._-]")


def document_root() -> Path:
    root = Path(settings.MEDIA_ROOT) / "education-documents"
    root.mkdir(parents=True, exist_ok=True)
    return root


def safe_filename(name: str) -> str:
    cleaned = SAFE_NAME.sub("-", Path(name or "application-document").name).strip(".")
    return (cleaned or "application-document")[-120:]


def has_valid_signature(content_type: str, data: bytes) -> bool:
    if content_type == "application/pdf":
        return data.startswith(b"%PDF-")
    if content_type == "image/jpeg":
        return data.startswith(b"\xff\xd8\xff")
    if content_type == "image/png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if content_type == "image/webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    return False


def local_document_path(key: str) -> Path | None:
    prefix = "education-documents/"
    if not key.startswith(prefix) or ".." in Path(key).parts:
        return None
    root = document_root().resolve()
    candidate = (root / key[len(prefix):]).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


class EducationDocumentUploadView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded = request.FILES.get("file")
        if not uploaded:
            return Response({"detail": "Please attach a PDF or education-document photo."}, status=status.HTTP_400_BAD_REQUEST)
        if uploaded.size > MAX_DOCUMENT_BYTES:
            return Response({"detail": "Each document must be 10 MB or smaller."}, status=status.HTTP_400_BAD_REQUEST)
        content_type = (uploaded.content_type or mimetypes.guess_type(uploaded.name)[0] or "").lower()
        if content_type not in ALLOWED_TYPES:
            return Response({"detail": "Only PDF, JPG, PNG, or WebP files are accepted."}, status=status.HTTP_400_BAD_REQUEST)
        sample = uploaded.read(64)
        uploaded.seek(0)
        if not has_valid_signature(content_type, sample):
            return Response({"detail": "The uploaded file does not match its declared document type."}, status=status.HTTP_400_BAD_REQUEST)
        category = str(request.data.get("category", "supporting")).strip().lower()
        if category not in ALLOWED_CATEGORIES:
            category = "supporting"
        key = f"education-documents/{category}/{uuid4()}-{safe_filename(uploaded.name)}"
        target = local_document_path(key)
        if target is None:
            return Response({"detail": "The document path is invalid."}, status=status.HTTP_400_BAD_REQUEST)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as destination:
            for chunk in uploaded.chunks():
                destination.write(chunk)
        return Response({"name": uploaded.name, "content_type": content_type, "size": uploaded.size, "category": category, "key": key, "url": f"/manus-storage/{key}"}, status=status.HTTP_201_CREATED)


class StaffDocumentServeView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    def get(self, request, key):
        path = local_document_path(key)
        if path is None or not path.is_file():
            raise Http404("Document not found.")
        return FileResponse(path.open("rb"), as_attachment=False, filename=path.name)

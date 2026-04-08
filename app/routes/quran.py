from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException

from app.services.quran_api import QuranAPIClient
from app.services.qurancom_api import QuranComAPI

router = APIRouter(prefix="/api/quran", tags=["quran"])
quran_client = QuranAPIClient()
qurancom_client = QuranComAPI()


@router.get("/chapters")
async def get_chapters(language: str = "fr"):
    """Récupérer toutes les sourates"""
    try:
        return await quran_client.get_chapters(language)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/chapters/{chapter_id}/verses")
async def get_chapter_verses(
    chapter_id: int,
    language: str = "fr",
    translations: Optional[str] = None,
    words: bool = True,
    per_page: int = 50,
):
    """
    Récupérer les versets d'une sourate avec texte Unicode normal
    
    NOUVEAU : Utilise une fusion de quran.com (texte Unicode) 
    et Quran.Foundation (traductions)
    """
    try:
        # Utiliser la fusion pour obtenir du texte Unicode normal
        return await qurancom_client.get_verses_merged(
            chapter_id=chapter_id,
            quran_foundation_client=quran_client,
            language=language,
            translations=translations or "131",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/chapters/{chapter_id}/verses/uthmani")
async def get_chapter_verses_uthmani(
    chapter_id: int,
    translations: str = "131",
):
    """
    Récupérer les versets avec texte Uthmani en Unicode normal
    Utilise l'API publique quran.com qui retourne du texte Unicode standard
    """
    try:
        return await qurancom_client.get_verses_with_uthmani(chapter_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/translations")
async def get_translations(language: str = "fr"):
    """Récupérer les traductions disponibles"""
    try:
        return await quran_client.get_translations(language)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/recitations")
async def get_recitations():
    """Récupérer les récitants"""
    try:
        return await quran_client.get_recitations()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/recitations/{reciter_id}/chapter/{chapter_id}")
async def get_chapter_audio(reciter_id: int, chapter_id: int):
    """Récupérer l'audio d'une sourate"""
    try:
        return await quran_client.get_chapter_audio(reciter_id, chapter_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/search")
async def search_quran(
    q: str,
    language: str = "fr",
    page: int = 1,
    size: int = 20,
):
    """
    Rechercher dans le Coran.
    Nécessite le scope 'search' (non disponible en pré-prod pour la plupart des clients).
    """
    try:
        return await quran_client.search_quran(q, language, page, size)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (401, 403):
            raise HTTPException(
                status_code=e.response.status_code,
                detail=(
                    "Le scope 'search' n'est pas disponible en pré-production. "
                    "Contactez Quran Foundation pour l'activer."
                ),
            ) from e
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

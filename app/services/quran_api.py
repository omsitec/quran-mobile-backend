import base64
import logging
import time
from typing import Any, Dict, Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _normalize_content_endpoint(url: str) -> str:
    """Normalise les anciennes bases URL vers les hôtes officiels (quickstart QF)."""
    u = url.rstrip("/")
    if "prelive-api.quran.foundation" in u:
        u = u.replace(
            "prelive-api.quran.foundation",
            "apis-prelive.quran.foundation",
        )
        logger.warning("URL content normalisée vers apis-prelive: %s", u)
    if "api.quran.foundation" in u and "apis." not in u:
        u = u.replace("api.quran.foundation", "apis.quran.foundation")
        logger.warning("URL content normalisée vers apis: %s", u)
    return u


class QuranAPIClient:
    def __init__(self):
        self.client_id = settings.quran_api_client_id.strip()
        self.client_secret = settings.quran_api_client_secret.strip()
        self.oauth_endpoint = settings.quran_api_oauth_endpoint.rstrip("/")
        self.scopes = settings.quran_api_oauth_scopes.strip() or "content"

        self.content_endpoint = _normalize_content_endpoint(
            settings.quran_api_content_endpoint
        )
        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0.0

    def _is_token_expired(self) -> bool:
        return time.time() >= self.token_expires_at

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Access token (client_credentials) avec HTTP Basic Auth.
        POST {oauth}/oauth2/token — pas /oauth2/v1/token.
        """
        if self.access_token and not self._is_token_expired() and not force_refresh:
            return self.access_token

        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_b64 = base64.b64encode(auth_string.encode("ascii")).decode("ascii")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.oauth_endpoint}/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "scope": self.scopes,
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Authorization": f"Basic {auth_b64}",
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                self.access_token = data["access_token"]
                expires_in = int(data.get("expires_in", 3600))
                self.token_expires_at = time.time() + expires_in - 60

                logger.info("Token OAuth obtenu, expire dans %ss", expires_in)
                return self.access_token

            except httpx.HTTPStatusError as e:
                logger.error(
                    "Erreur OAuth2: %s - %s",
                    e.response.status_code,
                    e.response.text,
                )
                raise Exception(
                    f"Échec authentification OAuth2: {e.response.text}"
                ) from e

    async def _get_headers(self) -> Dict[str, str]:
        if not self.access_token or self._is_token_expired():
            await self.get_access_token()

        return {
            "x-auth-token": self.access_token or "",
            "x-client-id": self.client_id,
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        retry_on_401: bool = True,
    ) -> Dict[str, Any]:
        """Requête vers l'API ; en cas de 401, invalide le token et réessaie une fois."""
        headers = await self._get_headers()
        url = f"{self.content_endpoint}{endpoint}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    timeout=60.0,
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401 and retry_on_401:
                    logger.warning("401 détecté, nouvelle demande de token…")
                    self.access_token = None
                    self.token_expires_at = 0.0
                    return await self._make_request(
                        method, endpoint, params, retry_on_401=False
                    )
                raise

    async def get_chapters(self, language: str = "fr") -> Dict[str, Any]:
        return await self._make_request(
            "GET",
            "/content/api/v4/chapters",
            params={"language": language},
        )

    async def get_chapter_verses(
        self,
        chapter_id: int,
        language: str = "fr",
        translations: Optional[str] = None,
        words: bool = True,
        per_page: int = 50,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "language": language,
            "words": str(words).lower(),
            "per_page": per_page,
        }
        if translations:
            params["translations"] = translations

        return await self._make_request(
            "GET",
            f"/content/api/v4/verses/by_chapter/{chapter_id}",
            params=params,
        )

    async def get_translations(self, language: str = "fr") -> Dict[str, Any]:
        return await self._make_request(
            "GET",
            "/content/api/v4/resources/translations",
            params={"language": language},
        )

    async def get_recitations(self) -> Dict[str, Any]:
        return await self._make_request(
            "GET",
            "/content/api/v4/resources/recitations",
        )

    async def get_chapter_audio(
        self,
        reciter_id: int,
        chapter_id: int,
    ) -> Dict[str, Any]:
        return await self._make_request(
            "GET",
            f"/content/api/v4/chapter_recitations/{reciter_id}/by_chapter/{chapter_id}",
        )

    async def search_quran(
        self,
        query: str,
        language: str = "fr",
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        """
        Nécessite le scope « search » (souvent indisponible en pré-prod).
        """
        size = max(1, min(int(size), 50))
        return await self._make_request(
            "GET",
            "/search/v1/search",
            params={
                "q": query,
                "language": language,
                "page": page,
                "size": size,
            },
        )

"""
Service pour récupérer le texte arabe depuis l'API publique quran.com
Cette API retourne le texte en Unicode normal (pas de codes PUA)
"""
import httpx
from typing import Dict, Any


class QuranComAPI:
    """Client pour l'API publique quran.com v4"""
    
    BASE_URL = "https://api.quran.com/api/v4"
    
    async def get_verses_with_uthmani(
        self,
        chapter_id: int,
        translations: str = "131",  # French translation par défaut
    ) -> Dict[str, Any]:
        """
        Récupère les versets avec texte Uthmani normal
        
        Args:
            chapter_id: Numéro de la sourate (1-114)
            translations: IDs des traductions séparées par virgule
            
        Returns:
            Dict avec les versets et le texte arabe en Unicode normal
        """
        async with httpx.AsyncClient() as client:
            # Récupérer les versets avec le texte Uthmani
            response = await client.get(
                f"{self.BASE_URL}/verses/by_chapter/{chapter_id}",
                params={
                    "words": "false",
                    "translations": translations,
                    "per_page": 300,  # Max pour récupérer toute la sourate
                    "fields": "text_uthmani",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

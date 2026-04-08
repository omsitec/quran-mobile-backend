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
    ) -> Dict[str, Any]:
        """
        Récupère les versets avec texte Uthmani normal
        
        Args:
            chapter_id: Numéro de la sourate (1-114)
            
        Returns:
            Dict avec les versets et le texte arabe en Unicode normal
        """
        async with httpx.AsyncClient() as client:
            # Récupérer les versets avec le texte Uthmani
            response = await client.get(
                f"{self.BASE_URL}/verses/by_chapter/{chapter_id}",
                params={
                    "words": "false",
                    "per_page": 300,  # Max pour récupérer toute la sourate
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_verses_merged(
        self,
        chapter_id: int,
        quran_foundation_client,
        language: str = "fr",
        translations: str = "131",
    ) -> Dict[str, Any]:
        """
        Fusionne les données de quran.com (texte Unicode normal) 
        et Quran.Foundation (traductions et métadonnées)
        
        Args:
            chapter_id: Numéro de la sourate (1-114)
            quran_foundation_client: Instance de QuranAPIClient
            language: Langue pour les traductions
            translations: IDs des traductions
            
        Returns:
            Dict avec versets fusionnés : texte Unicode + traductions
        """
        # 1. Récupérer le texte Unicode normal de quran.com
        qurancom_data = await self.get_verses_with_uthmani(chapter_id)
        
        # 2. Récupérer les traductions de Quran.Foundation (sans words)
        qf_data = await quran_foundation_client.get_chapter_verses(
            chapter_id=chapter_id,
            language=language,
            translations=translations,
            words=False,  # On ne veut pas les mots avec codes PUA
            per_page=300,
        )
        
        # 3. Créer un dictionnaire verse_number -> verse pour accès rapide
        qf_verses_dict = {
            v.get("verse_number"): v 
            for v in qf_data.get("verses", [])
        }
        
        # 4. Fusionner les données
        merged_verses = []
        for verse in qurancom_data.get("verses", []):
            verse_number = verse.get("verse_number")
            
            # Ajouter les métadonnées et traductions de Quran.Foundation
            if verse_number in qf_verses_dict:
                qf_verse = qf_verses_dict[verse_number]
                
                # Garder le texte Unicode de quran.com
                verse["text_uthmani"] = verse.get("text_uthmani", "")
                
                # Ajouter les traductions de Quran.Foundation
                verse["translations"] = qf_verse.get("translations", [])
                
                # Ajouter les métadonnées manquantes
                verse["verse_key"] = qf_verse.get("verse_key", f"{chapter_id}:{verse_number}")
                verse["hizb_number"] = qf_verse.get("hizb_number")
                verse["rub_el_hizb_number"] = qf_verse.get("rub_el_hizb_number")
                verse["ruku_number"] = qf_verse.get("ruku_number")
                verse["manzil_number"] = qf_verse.get("manzil_number")
                verse["sajdah_number"] = qf_verse.get("sajdah_number")
            
            merged_verses.append(verse)
        
        return {"verses": merged_verses}

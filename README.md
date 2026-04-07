# Quran Mobile - Backend API

Backend FastAPI pour l'application Quran Mobile.

## Dépannage 401 (chapters / content)

- **URL API** : utiliser `https://apis-prelive.quran.foundation` (et en prod `https://apis.quran.foundation`), pas `prelive-api` / `api.` seuls — voir [quickstart officiel](https://api-docs.quran.foundation/docs/quickstart).
- **Token OAuth** : `POST .../oauth2/token` avec **HTTP Basic** (`client_id` / `client_secret`) et corps `grant_type=client_credentials&scope=...` (pas seulement le secret dans le corps).
- **Scope recherche** : le scope `search` n’est pas toujours accordé aux clients pré-prod ; laisser `QURAN_API_OAUTH_SCOPES=content` par défaut.

## Installation

1. Créer un environnement virtuel:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Installer les dépendances:
```bash
pip install -r requirements.txt
```
   Sous **Python 3.14** (Windows), les versions épinglées de `pydantic` peuvent exiger Rust pour compiler : préférez **Python 3.11 ou 3.12**, ou suivez le commentaire en bas de `requirements.txt`.

3. Configurer les variables d'environnement:
```bash
copy .env.example .env
# Éditer .env avec vos valeurs
```

4. Lancer le serveur:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## Documentation API

Accéder à la documentation Swagger: http://localhost:8000/docs

## Endpoints

### Quran
- `GET /api/quran/chapters` - Liste des sourates
- `GET /api/quran/chapters/{id}/verses` - Versets d'une sourate
- `GET /api/quran/translations` - Traductions disponibles
- `GET /api/quran/recitations` - Récitants disponibles
- `GET /api/quran/recitations/{reciter_id}/chapter/{chapter_id}` - Audio
- `GET /api/quran/search` - Recherche

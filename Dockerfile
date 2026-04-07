# Backend FastAPI pour Quran Mobile
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code de l'application
COPY ./app ./app

# Exposer le port 8000
EXPOSE 8000

# Variable d'environnement pour production
ENV PYTHONUNBUFFERED=1

# Commande pour démarrer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

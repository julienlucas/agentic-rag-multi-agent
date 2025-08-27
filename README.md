Ajoutez une étoile au repo pour soutenir mon travail. 🙏

# RAG Agentique (supérieur en précision au RAS classique) avec récupérateur avancé pour une recherche de documents (meilleur que GPT4o et DeepSeek R1)

## Comment fonctionn l'app
Voici un diagramme.
![Projet Overview](./assets/project-overview.jpg)

## Installation

1. **Cloner le projet** :
```bash
git clone https://github.com/julienlucas/agentic-rag-multi-agent
```

2. **Installer les dépendances** :
```bash
python3.12 -m venv venv
source venv/bin/activate
# Backend Django
poetry install
```

3. **Configuration** :
Allez sur https://console.mistral.ai pour créer votre clé API
Créez un fichier `.env` avec vos clés API :
```bash
MISTRALAI_API_KEY=votre_clé_api_mistral_ici
```

4. **Lancer l'application** :
```bash
python app.py
```
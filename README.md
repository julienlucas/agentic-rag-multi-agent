Ajoutez une étoile au repo pour soutenir mon travail. 🙏

# RAG Agentique multi-agent de document (meilleur que GPT4o et DeepSeek R1)

## Comment fonctionne l'app

Ce système RAG agentique fonctionne avec 3 agents spécialisés et un récupérateur avancé (BM25 + embeddings) garantissant une haute précision.

![Projet Overview](./assets/project-overview.jpg)

### Architecture des 3 agents

#### 1. **Agent de Recherche**
Analyse la question utilisateur et recherche

#### 2. **Vérificateur de Pertinence**
Évalue si le document récupéré répond réellement à la question

#### 3. **Agent Fact Checker**
Valide et croise les informations trouvées

### Récupérateur Hybride pour un maximum de pertinence
- **Algo BM25 + Embeddings** : Recherche texte classique à forte précision lexicale + Recherche sémantique capturant le sens contextuel

## Installation

1. **Cloner le projet** :
```bash
git clone https://github.com/julienlucas/agentic-rag-multi-agent
```

2. **Installer les dépendances** :
```bash
python3.12 -m venv venv
source venv/bin/activate
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
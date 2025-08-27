import os
import hashlib
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from docling.document_converter import DocumentConverter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from config import constants
from config.settings import settings
from utils.logging import logger

class DocumentProcessor:
    def __init__(self):
        self.headers = [("#", "Header 1"), ("##", "Header 2")]
        self.cache_dir = Path(settings.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _validate_files(self, files: List) -> None:
        """Valider la taille totale des fichiers téléchargés."""
        total_size = sum(os.path.getsize(f.name) for f in files)
        if total_size > constants.MAX_TOTAL_SIZE:
            raise ValueError(f"La taille totale dépasse la limite de {constants.MAX_TOTAL_SIZE//1024//1024}MB")

    def process(self, files: List) -> List:
        """Traiter les fichiers avec mise en cache pour les requêtes suivantes"""
        self._validate_files(files)
        all_chunks = []
        seen_hashes = set()

        for file in files:
            try:
                # Générer un hachage basé sur le contenu pour la mise en cache
                with open(file.name, "rb") as f:
                    file_hash = self._generate_hash(f.read())
                cache_path = self.cache_dir / f"{file_hash}.pkl"

                if self._is_cache_valid(cache_path):
                    logger.info(f"Chargement depuis le cache: {file.name}")
                    chunks = self._load_from_cache(cache_path)
                else:
                    logger.info(f"Traitement et mise en cache: {file.name}")
                    chunks = self._process_file(file)
                    self._save_to_cache(chunks, cache_path)

                # Dédupliquer les chunks entre les fichiers
                for chunk in chunks:
                    chunk_hash = self._generate_hash(chunk.page_content.encode())
                    if chunk_hash not in seen_hashes:
                        all_chunks.append(chunk)
                        seen_hashes.add(chunk_hash)

            except Exception as e:
                logger.error(f"Échec du traitement de {file.name}: {str(e)}")
                continue

        logger.info(f"Total des chunks uniques: {len(all_chunks)}")
        return all_chunks

    def _process_file(self, file) -> List:
        """Logique de traitement originale avec Docling"""
        if not file.name.endswith(('.pdf', '.docx', '.txt', '.md')):
            logger.warning(f"Ignorer le type de fichier non supporté: {file.name}")
            return []

        converter = DocumentConverter()
        markdown = converter.convert(file.name).document.export_to_markdown()
        splitter = MarkdownHeaderTextSplitter(self.headers)
        return splitter.split_text(markdown)

    def _generate_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def _save_to_cache(self, chunks: List, cache_path: Path):
        with open(cache_path, "wb") as f:
            pickle.dump({
                "timestamp": datetime.now().timestamp(),
                "chunks": chunks
            }, f)

    def _load_from_cache(self, cache_path: Path) -> List:
        with open(cache_path, "rb") as f:
            data = pickle.load(f)
        return data["chunks"]

    def _is_cache_valid(self, cache_path: Path) -> bool:
        if not cache_path.exists():
            return False
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return cache_age < timedelta(days=settings.CACHE_EXPIRE_DAYS)
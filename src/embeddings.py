"""
Text embedding support for recommender.py.

Provides a cached, disk-persisted way to turn short text (genre/mood strings)
into Gemini embedding vectors, plus a cosine similarity helper. Kept separate
from recommender.py so the scoring logic isn't tangled up with API/cache
plumbing.
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Protocol


class EmbeddingClient(Protocol):
    """Anything that can turn text into an embedding vector."""

    def embed(self, text: str) -> List[float]:
        ...


class GeminiEmbeddingClient:
    """Embeds text using the Gemini API (google-genai SDK)."""

    def __init__(
        self,
        model: str = "gemini-embedding-001",
        output_dimensionality: int = 768,
    ):
        self._model = model
        self._output_dimensionality = output_dimensionality
        self._client = None  # constructed lazily so import/construction never requires an API key

    def _get_client(self):
        if self._client is None:
            import os
            from dotenv import load_dotenv
            from google import genai

            load_dotenv()
            api_key = os.environ["GEMINI_API_KEY"]
            self._client = genai.Client(api_key=api_key)
        return self._client

    def embed(self, text: str) -> List[float]:
        from google.genai import types

        client = self._get_client()
        response = client.models.embed_content(
            model=self._model,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="SEMANTIC_SIMILARITY",
                output_dimensionality=self._output_dimensionality,
            ),
        )
        return response.embeddings[0].values


class EmbeddingCache:
    """
    Caches text -> embedding vector on disk, keyed by the text itself (not by
    song id), so repeated genre/mood strings across songs and user profiles
    only ever get embedded once.
    """

    def __init__(self, client: EmbeddingClient, cache_path: Path):
        self._client = client
        self._cache_path = cache_path
        self._cache: Dict[str, List[float]] = {}
        if cache_path.exists():
            with open(cache_path, encoding="utf-8") as f:
                self._cache = json.load(f)

    def get(self, text: str) -> List[float]:
        key = text.strip().lower()
        if key not in self._cache:
            self._cache[key] = self._client.embed(key)
            self._save()
        return self._cache[key]

    def _save(self) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._cache_path, "w", encoding="utf-8") as f:
            json.dump(self._cache, f)


_DEFAULT_CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "embeddings_cache.json"


def default_embedding_cache() -> EmbeddingCache:
    """The real, Gemini-backed cache used by Recommender when no cache is injected."""
    return EmbeddingCache(GeminiEmbeddingClient(), _DEFAULT_CACHE_PATH)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors, clamped to [0, 1] for use as a scoring multiplier."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


def text_similarity(text_a: str, text_b: str, cache: EmbeddingCache) -> float:
    """Embedding-based similarity between two pieces of text, using the given cache."""
    if text_a.strip().lower() == text_b.strip().lower():
        return 1.0
    return cosine_similarity(cache.get(text_a), cache.get(text_b))

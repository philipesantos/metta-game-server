from dataclasses import dataclass
from threading import Lock

import numpy as np
from sentence_transformers import SentenceTransformer

from core.nlp.command_catalog import CommandEntry


@dataclass(frozen=True)
class MatchResult:
    entry: CommandEntry
    score: float


_MODEL_CACHE_LOCK = Lock()
_MODEL_CACHE: dict[str, SentenceTransformer] = {}
_TEXT_EMBEDDING_CACHE: dict[str, dict[str, np.ndarray]] = {}


def _get_shared_sentence_transformer(model_name: str) -> SentenceTransformer:
    with _MODEL_CACHE_LOCK:
        model = _MODEL_CACHE.get(model_name)
        if model is None:
            model = SentenceTransformer(model_name)
            _MODEL_CACHE[model_name] = model
        return model


def _clear_shared_sentence_transformer_cache() -> None:
    with _MODEL_CACHE_LOCK:
        _MODEL_CACHE.clear()
        _TEXT_EMBEDDING_CACHE.clear()


class EmbeddingIndex:
    def __init__(
        self,
        entries: list[CommandEntry],
        model_name: str,
        *,
        min_score: float = 0.55,
        min_margin: float = 0.06,
        high_confidence_score: float = 0.82,
    ):
        self.entries = entries
        self.model_name = model_name
        self.min_score = min_score
        self.min_margin = min_margin
        self.high_confidence_score = high_confidence_score
        self.model = _get_shared_sentence_transformer(model_name)
        self.embeddings = self._build_embeddings(entries)

    def update_entries(self, entries: list[CommandEntry]) -> None:
        self.entries = entries
        self.embeddings = self._build_embeddings(entries)

    def _build_embeddings(self, entries: list[CommandEntry]) -> np.ndarray:
        if not entries:
            return np.empty((0, 0), dtype=np.float32)
        texts = [entry.utterance for entry in entries]
        with _MODEL_CACHE_LOCK:
            shared_cache = _TEXT_EMBEDDING_CACHE.setdefault(self.model_name, {})
            missing_texts = [text for text in texts if text not in shared_cache]
        if missing_texts:
            missing_embeddings = self.model.encode(
                missing_texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            with _MODEL_CACHE_LOCK:
                shared_cache = _TEXT_EMBEDDING_CACHE.setdefault(self.model_name, {})
                for text, embedding in zip(missing_texts, missing_embeddings):
                    shared_cache.setdefault(text, embedding)

        with _MODEL_CACHE_LOCK:
            return np.array(
                [_TEXT_EMBEDDING_CACHE[self.model_name][text] for text in texts],
                dtype=np.float32,
            )

    def match(self, query: str) -> MatchResult | None:
        if not self.entries:
            return None
        normalized_query = query.strip()
        if not normalized_query:
            return None

        exact_matches = [
            entry
            for entry in self.entries
            if entry.utterance.casefold() == normalized_query.casefold()
        ]
        if len(exact_matches) == 1:
            return MatchResult(entry=exact_matches[0], score=1.0)

        query_vec = self.model.encode(
            [normalized_query],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )[0]
        scores = self.embeddings @ query_vec
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        if best_score < self.min_score:
            return None

        if len(scores) > 1:
            sorted_scores = np.sort(scores)
            second_best = float(sorted_scores[-2])
            if (
                best_score < self.high_confidence_score
                and (best_score - second_best) < self.min_margin
            ):
                return None

        best_entry = self.entries[best_idx]
        overlap_count = _token_overlap_count(normalized_query, best_entry.utterance)
        if best_score < self.high_confidence_score and overlap_count == 0:
            return None

        return MatchResult(entry=best_entry, score=best_score)


_STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "do",
    "for",
    "i",
    "in",
    "is",
    "me",
    "my",
    "of",
    "on",
    "please",
    "the",
    "to",
    "what",
    "with",
}


def _tokenize(text: str) -> set[str]:
    words = "".join(char.lower() if char.isalnum() else " " for char in text).split()
    return {word for word in words if len(word) > 1 and word not in _STOPWORDS}


def _token_overlap_count(left: str, right: str) -> int:
    return len(_tokenize(left).intersection(_tokenize(right)))

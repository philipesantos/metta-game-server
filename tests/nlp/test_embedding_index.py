import unittest
from unittest.mock import patch

import numpy as np

from core.nlp import CommandEntry, EmbeddingIndex


class _FakeSentenceTransformer:
    def __init__(self, vectors: dict[str, np.ndarray]):
        self._vectors = vectors
        self.calls: list[list[str]] = []

    def encode(
        self,
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ):
        self.calls.append(list(texts))
        vectors = np.array([self._vectors[text] for text in texts], dtype=np.float32)
        if normalize_embeddings:
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms[norms == 0.0] = 1.0
            vectors = vectors / norms
        return vectors if convert_to_numpy else vectors.tolist()


class TestEmbeddingIndex(unittest.TestCase):
    def test_matches_best_entry_for_query(self):
        entries = [
            CommandEntry(
                utterance="pickup compass",
                intent="pickup",
                metta="(pickup (compass))",
                slots={"item": "compass"},
            ),
            CommandEntry(
                utterance="drop compass",
                intent="drop",
                metta="(drop (compass))",
                slots={"item": "compass"},
            ),
        ]
        vectors = {
            "pickup compass": np.array([1.0, 0.0], dtype=np.float32),
            "drop compass": np.array([0.8, 0.2], dtype=np.float32),
            "pickup compass now": np.array([0.99, 0.01], dtype=np.float32),
        }

        with patch(
            "core.nlp.embedding_index.SentenceTransformer",
            return_value=_FakeSentenceTransformer(vectors),
        ):
            index = EmbeddingIndex(entries, model_name="fake")
            match = index.match("pickup compass now")

        self.assertIsNotNone(match)
        self.assertEqual(match.entry.utterance, "pickup compass")

    def test_returns_none_for_low_confidence_match(self):
        entries = [
            CommandEntry(
                utterance="inventory",
                intent="inventory",
                metta="(inventory)",
                slots={},
            )
        ]
        vectors = {
            "inventory": np.array([1.0, 0.0], dtype=np.float32),
            "nonsense words": np.array([0.2, 1.0], dtype=np.float32),
        }

        with patch(
            "core.nlp.embedding_index.SentenceTransformer",
            return_value=_FakeSentenceTransformer(vectors),
        ):
            index = EmbeddingIndex(entries, model_name="fake", min_score=0.6)
            match = index.match("nonsense words")

        self.assertIsNone(match)

    def test_returns_none_for_ambiguous_match(self):
        entries = [
            CommandEntry(
                utterance="go north",
                intent="move_towards",
                metta="(move-towards (north))",
                slots={"direction": "north"},
            ),
            CommandEntry(
                utterance="go south",
                intent="move_towards",
                metta="(move-towards (south))",
                slots={"direction": "south"},
            ),
        ]
        vectors = {
            "go north": np.array([1.0, 0.0], dtype=np.float32),
            "go south": np.array([0.0, 1.0], dtype=np.float32),
            "go maybe": np.array([0.71, 0.70], dtype=np.float32),
        }

        with patch(
            "core.nlp.embedding_index.SentenceTransformer",
            return_value=_FakeSentenceTransformer(vectors),
        ):
            index = EmbeddingIndex(
                entries,
                model_name="fake",
                min_margin=0.05,
                high_confidence_score=0.99,
            )
            match = index.match("go maybe")

        self.assertIsNone(match)

    def test_returns_none_when_no_token_overlap_and_not_high_confidence(self):
        entries = [
            CommandEntry(
                utterance="inventory",
                intent="inventory",
                metta="(inventory)",
                slots={},
            )
        ]
        vectors = {
            "inventory": np.array([1.0, 0.0], dtype=np.float32),
            "hello there": np.array([0.8, 0.6], dtype=np.float32),
        }

        with patch(
            "core.nlp.embedding_index.SentenceTransformer",
            return_value=_FakeSentenceTransformer(vectors),
        ):
            index = EmbeddingIndex(
                entries, model_name="fake", high_confidence_score=0.9
            )
            match = index.match("hello there")

        self.assertIsNone(match)

    def test_allows_no_token_overlap_when_score_is_high_confidence(self):
        entries = [
            CommandEntry(
                utterance="inventory",
                intent="inventory",
                metta="(inventory)",
                slots={},
            )
        ]
        vectors = {
            "inventory": np.array([1.0, 0.0], dtype=np.float32),
            "status please": np.array([1.0, 0.0], dtype=np.float32),
        }

        with patch(
            "core.nlp.embedding_index.SentenceTransformer",
            return_value=_FakeSentenceTransformer(vectors),
        ):
            index = EmbeddingIndex(
                entries, model_name="fake", high_confidence_score=0.9
            )
            match = index.match("status please")

        self.assertIsNotNone(match)
        self.assertEqual(match.entry.utterance, "inventory")

    def test_update_entries_reuses_cached_embeddings_for_existing_utterances(self):
        initial_entries = [
            CommandEntry(
                utterance="pickup compass",
                intent="pickup",
                metta="(pickup (compass))",
                slots={"item": "compass"},
            )
        ]
        updated_entries = [
            initial_entries[0],
            CommandEntry(
                utterance="pickup lantern",
                intent="pickup",
                metta="(pickup (lantern))",
                slots={"item": "lantern"},
            ),
        ]
        vectors = {
            "pickup compass": np.array([1.0, 0.0], dtype=np.float32),
            "pickup lantern": np.array([0.0, 1.0], dtype=np.float32),
        }
        fake_model = _FakeSentenceTransformer(vectors)

        with patch(
            "core.nlp.embedding_index.SentenceTransformer",
            return_value=fake_model,
        ):
            index = EmbeddingIndex(initial_entries, model_name="fake")
            index.update_entries(updated_entries)

        self.assertEqual(fake_model.calls[0], ["pickup compass"])
        self.assertEqual(fake_model.calls[1], ["pickup lantern"])


if __name__ == "__main__":
    unittest.main()

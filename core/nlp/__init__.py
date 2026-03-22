from core.nlp.command_catalog import CommandEntry, build_command_catalog
from core.nlp.nl_spec import NLSpec, SlotSpec

try:
    from core.nlp.embedding_index import EmbeddingIndex, MatchResult
except ModuleNotFoundError:
    EmbeddingIndex = None
    MatchResult = None

__all__ = [
    "CommandEntry",
    "EmbeddingIndex",
    "MatchResult",
    "NLSpec",
    "SlotSpec",
    "build_command_catalog",
]

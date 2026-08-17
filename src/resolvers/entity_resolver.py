import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EntityMapping:
    raw_name: str
    canonical_name: str
    confidence: float
    method: str


def normalize_name(name: str) -> str:
    """
    Normalize an entity name for deterministic comparison.
    """

    value = name.strip().casefold()

    value = re.sub(
        r"[^\w\s]",
        " ",
        value,
    )

    value = re.sub(
        r"\b(inc|incorporated|llc|ltd|limited|corp|corporation)\b",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


class EntityResolver:
    """
    Deterministic entity resolver.

    No LLM-generated canonical names are allowed.
    Canonical names must come from the supplied seed list.
    """

    def __init__(
        self,
        canonical_entities: list[str],
    ):

        self.canonical_entities = canonical_entities

        self.normalized_map = {
            normalize_name(entity): entity
            for entity in canonical_entities
        }

    def resolve(
        self,
        raw_name: str,
    ) -> EntityMapping:

        normalized = normalize_name(
            raw_name
        )

        canonical = self.normalized_map.get(
            normalized
        )

        if canonical:

            return EntityMapping(
                raw_name=raw_name,
                canonical_name=canonical,
                confidence=1.0,
                method="normalized_exact_match",
            )

        return EntityMapping(
            raw_name=raw_name,
            canonical_name=raw_name.strip(),
            confidence=0.0,
            method="unresolved",
        )
def mapping_to_record(
    mapping: EntityMapping,
    source_url: str,
) -> dict:
    """
    Convert an entity mapping into an auditable
    JSON-compatible record.
    """

    return {
        "raw_name": mapping.raw_name,
        "canonical_name": mapping.canonical_name,
        "confidence": mapping.confidence,
        "method": mapping.method,
        "source_url": source_url,
    }
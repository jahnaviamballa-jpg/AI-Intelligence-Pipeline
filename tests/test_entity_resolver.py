from src.resolvers.entity_resolver import (
    EntityResolver,
    normalize_name,
)


def test_normalize_name():

    assert (
        normalize_name("OpenAI, Inc.")
        == "openai"
    )

    assert (
        normalize_name("Open AI")
        == "open ai"
    )


def test_resolve_exact_canonical_name():

    resolver = EntityResolver(
        ["OpenAI", "Anthropic", "Google"]
    )

    result = resolver.resolve(
        "OpenAI"
    )

    assert result.canonical_name == "OpenAI"
    assert result.confidence == 1.0


def test_resolve_company_suffix():

    resolver = EntityResolver(
        ["OpenAI", "Anthropic", "Google"]
    )

    result = resolver.resolve(
        "OpenAI, Inc."
    )

    assert result.canonical_name == "OpenAI"
    assert result.method == "normalized_exact_match"


def test_unresolved_entity():

    resolver = EntityResolver(
        ["OpenAI", "Anthropic"]
    )

    result = resolver.resolve(
        "Unknown AI Company"
    )

    assert result.canonical_name == "Unknown AI Company"
    assert result.confidence == 0.0
    assert result.method == "unresolved"
def test_mapping_to_record():

    from src.resolvers.entity_resolver import (
        mapping_to_record,
    )

    resolver = EntityResolver(
        ["OpenAI"]
    )

    mapping = resolver.resolve(
        "OpenAI, Inc."
    )

    record = mapping_to_record(
        mapping,
        "https://example.com/openai",
    )

    assert record["raw_name"] == "OpenAI, Inc."
    assert record["canonical_name"] == "OpenAI"
    assert record["confidence"] == 1.0
    assert record["method"] == "normalized_exact_match"
    assert (
        record["source_url"]
        == "https://example.com/openai"
    )
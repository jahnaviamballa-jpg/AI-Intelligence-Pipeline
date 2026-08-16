from src.enrichers.github_enricher import (
    extract_github_url,
    get_repository_key,
    parse_retry_after,
    parse_reset_timestamp,
    calculate_backoff,
)


def test_extract_github_url():

    text = """
    The implementation is available at
    https://github.com/example-user/example-repo
    """

    result = extract_github_url(text)

    assert (
        result
        == "https://github.com/example-user/example-repo"
    )


def test_extract_github_url_from_long_text():

    text = """
    This research paper presents an AI model.

    Source code:
    https://github.com/openai/example-project

    The project contains the complete implementation.
    """

    result = extract_github_url(text)

    assert (
        result
        == "https://github.com/openai/example-project"
    )


def test_extract_github_url_without_url():

    text = """
    This paper does not contain any source code
    repository.
    """

    result = extract_github_url(text)

    assert result is None


def test_extract_github_url_handles_trailing_punctuation():

    text = (
        "Code: "
        "https://github.com/user/repository."
    )

    result = extract_github_url(text)

    assert (
        result
        == "https://github.com/user/repository"
    )


def test_extract_github_url_handles_www():

    text = (
        "https://www.github.com/user/repository"
    )

    result = extract_github_url(text)

    assert (
        result
        == "https://github.com/user/repository"
    )


def test_get_repository_key():

    url = (
        "https://github.com/"
        "openai/example-project"
    )

    result = get_repository_key(url)

    assert result == "openai/example-project"


def test_get_repository_key_handles_trailing_punctuation():

    url = (
        "https://github.com/"
        "openai/example-project."
    )

    result = get_repository_key(url)

    assert result == "openai/example-project"


def test_get_repository_key_invalid_url():

    url = "https://github.com/openai"

    result = get_repository_key(url)

    assert result is None


def test_get_repository_key_empty_url():

    result = get_repository_key("")

    assert result is None


def test_parse_retry_after():

    assert parse_retry_after("10") == 10.0


def test_parse_retry_after_decimal():

    assert parse_retry_after("2.5") == 2.5


def test_parse_retry_after_invalid_value():

    assert parse_retry_after("invalid") is None


def test_parse_retry_after_missing_value():

    assert parse_retry_after(None) is None


def test_parse_reset_timestamp():

    assert (
        parse_reset_timestamp("1750000000")
        == 1750000000
    )


def test_parse_reset_timestamp_invalid_value():

    assert parse_reset_timestamp("invalid") is None


def test_parse_reset_timestamp_missing_value():

    assert parse_reset_timestamp(None) is None


def test_calculate_backoff_is_positive():

    delay = calculate_backoff(1)

    assert delay > 0


def test_calculate_backoff_increases_with_attempt():

    delay_one = calculate_backoff(1)

    delay_three = calculate_backoff(3)

    assert delay_three > delay_one
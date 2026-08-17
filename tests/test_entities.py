from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.models.entities import (
    JobEntity,
    NewsEntity,
    ProductEntity,
    Source,
    StartupEntity,
)


def test_startup_entity_valid():

    record = StartupEntity(
        source=Source(
            name="Y Combinator",
            url="https://www.ycombinator.com/companies",
        ),
        content={
            "entityName": "Example AI",
            "employeeCount": 25,
            "sourceUrl": "https://www.ycombinator.com/companies/example-ai",
        },
        collectedAt=datetime.now(timezone.utc),
    )

    assert record.recordType == "STARTUP"
    assert record.content.entityName == "Example AI"


def test_product_entity_valid():

    record = ProductEntity(
        source=Source(
            name="Example Source",
            url="https://example.com",
        ),
        content={
            "productName": "Example AI Tool",
            "startupName": "Example AI",
            "pricingModel": "FREEMIUM",
            "sourceUrl": "https://example.com/product",
        },
        collectedAt=datetime.now(timezone.utc),
    )

    assert record.recordType == "PRODUCT"


def test_job_entity_valid():

    record = JobEntity(
        source=Source(
            name="Example Jobs",
            url="https://example.com/jobs",
        ),
        content={
            "company": "Example AI",
            "date": datetime.now(timezone.utc),
            "is_remote": True,
            "role_family": "Engineering",
            "sourceUrl": "https://example.com/jobs/123",
        },
        collectedAt=datetime.now(timezone.utc),
    )

    assert record.recordType == "JOB"


def test_news_entity_valid():

    record = NewsEntity(
        source=Source(
            name="Example News",
            url="https://example.com/news",
        ),
        content={
            "title": "Example AI launches new product",
            "date": datetime.now(timezone.utc),
            "sourceUrl": "https://example.com/news/example",
            "fullText": "This is source-derived article text.",
        },
        collectedAt=datetime.now(timezone.utc),
    )

    assert record.recordType == "NEWS"


def test_startup_rejects_missing_source_url():

    with pytest.raises(ValidationError):

        StartupEntity(
            source={
                "name": "Example",
                "url": "https://example.com",
            },
            content={
                "entityName": "Example AI",
                "employeeCount": 10,
            },
            collectedAt=datetime.now(timezone.utc),
        )


def test_product_rejects_invalid_source_url():

    with pytest.raises(ValidationError):

        ProductEntity(
            source={
                "name": "Example",
                "url": "https://example.com",
            },
            content={
                "productName": "Example Product",
                "sourceUrl": "not-a-url",
            },
            collectedAt=datetime.now(timezone.utc),
        )
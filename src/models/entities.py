from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Source(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    name: str = Field(
        min_length=1
    )

    url: HttpUrl


class StartupContent(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    entityName: str = Field(
        min_length=1
    )

    employeeCount: int | None = Field(
        default=None,
        ge=0
    )

    sourceUrl: HttpUrl


class StartupEntity(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    schemaVersion: str = "1.0"
    recordType: str = "STARTUP"

    source: Source
    content: StartupContent
    collectedAt: datetime


class ProductContent(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    productName: str = Field(
        min_length=1
    )

    startupName: str | None = None

    pricingModel: str | None = None

    sourceUrl: HttpUrl


class ProductEntity(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    schemaVersion: str = "1.0"
    recordType: str = "PRODUCT"

    source: Source
    content: ProductContent
    collectedAt: datetime


class JobContent(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    company: str = Field(
        min_length=1
    )

    date: datetime

    is_remote: bool

    role_family: str = Field(
        min_length=1
    )

    sourceUrl: HttpUrl


class JobEntity(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    schemaVersion: str = "1.0"
    recordType: str = "JOB"

    source: Source
    content: JobContent
    collectedAt: datetime


class NewsContent(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    title: str = Field(
        min_length=1
    )

    date: datetime

    sourceUrl: HttpUrl

    fullText: str = Field(
        min_length=1
    )


class NewsEntity(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    schemaVersion: str = "1.0"
    recordType: str = "NEWS"

    source: Source
    content: NewsContent
    collectedAt: datetime
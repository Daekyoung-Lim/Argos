import os
from crewai import Agent
from crewai.tools import tool

from ...tools.azure_vision_tool import extract_text_from_url
from ...tools.exif_parser_tool import extract_exif_metadata
from ...tools.azure_sql_tool import execute_read_query, insert_audit_log, get_asset_with_distance
from ...config import get_settings

settings = get_settings()

os.environ["AZURE_API_KEY"] = settings.azure_openai_api_key
os.environ["AZURE_API_BASE"] = settings.azure_openai_endpoint
os.environ["AZURE_API_VERSION"] = settings.azure_openai_api_version


@tool("azure_vision_tool")
def vision_tool(image_url: str) -> dict:
    """Extract text and asset code from an image URL using Azure AI Vision OCR."""
    return extract_text_from_url(image_url)


@tool("exif_parser_tool")
def exif_tool(image_bytes_b64: str) -> dict:
    """Extract GPS coordinates and timestamp from base64-encoded image EXIF metadata."""
    import base64
    data = base64.b64decode(image_bytes_b64)
    return extract_exif_metadata(data)


@tool("azure_sql_read_tool")
def sql_read_tool(sql: str) -> list:
    """Execute a read-only SELECT query against Azure SQL Database and return results."""
    return execute_read_query(sql)


@tool("azure_sql_distance_tool")
def sql_distance_tool(data_json: str) -> dict:
    """
    Fetch asset info and calculate distance. Takes JSON string with keys:
    'asset_code' (str), 'detected_lat' (float), 'detected_lon' (float).
    """
    import json
    data = json.loads(data_json)
    result = get_asset_with_distance(data.get("asset_code"), data.get("detected_lat"), data.get("detected_lon"))
    return result if result else {"error": "Asset not found"}


@tool("azure_sql_insert_tool")
def sql_insert_tool(data_json: str) -> int:
    """Insert an audit log record into AuditLogs table. Takes JSON string of audit data."""
    import json
    data = json.loads(data_json)
    return insert_audit_log(data)


def make_vision_agent() -> Agent:
    return Agent(
        role="Vision Agent",
        goal="Extract the asset code (e.g. KT-AS-1016 or 2510157774) from the uploaded asset sticker photo using OCR.",
        backstory=(
            "You are an expert in computer vision and OCR. Given an image URL, "
            "you use Azure AI Vision to read all text and extract the unique asset code."
        ),
        tools=[vision_tool],
        verbose=False,
        allow_delegation=False,
        llm=f"azure/{settings.azure_openai_deployment}",
    )


def make_metadata_agent() -> Agent:
    return Agent(
        role="Metadata Agent",
        goal="Extract GPS coordinates and capture timestamp from the image EXIF metadata.",
        backstory=(
            "You are an expert in image metadata. Given base64-encoded image bytes, "
            "you extract GPS location and DateTimeOriginal from EXIF data."
        ),
        tools=[exif_tool],
        verbose=False,
        allow_delegation=False,
        llm=f"azure/{settings.azure_openai_deployment}",
    )


def make_db_reference_agent() -> Agent:
    return Agent(
        role="DB Reference Agent",
        goal="Look up the asset by its code and calculate the geographic distance to the detected location.",
        backstory=(
            "You are a database expert. You find the asset "
            "matching the extracted code and compute the geographic distance using the provided tool."
        ),
        tools=[sql_distance_tool, sql_read_tool],
        verbose=False,
        allow_delegation=False,
        llm=f"azure/{settings.azure_openai_deployment}",
    )


def make_verifier_agent() -> Agent:
    return Agent(
        role="Verifier Agent",
        goal=(
            "Validate the self-survey submission by checking: "
            "(1) extracted code matches asset code, "
            "(2) detected location is within 3000m, "
            "(3) photo timestamp is within 48 hours."
        ),
        backstory=(
            "You are a strict compliance verifier for asset management. "
            "You apply the three validation rules and output JSON."
        ),
        tools=[],
        verbose=False,
        allow_delegation=False,
        llm=f"azure/{settings.azure_openai_deployment}",
    )

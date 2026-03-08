import re
from typing import Optional

from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

from ..config import get_settings

settings = get_settings()


def extract_text_from_url(image_url: str) -> dict:
    """
    Call Azure AI Vision Read API on the given URL.
    Returns {"raw_text": str, "asset_code": str | None}
    """
    client = ImageAnalysisClient(
        endpoint=settings.azure_ai_vision_endpoint,
        credential=AzureKeyCredential(settings.azure_ai_vision_api_key),
    )
    result = client.analyze_from_url(
        image_url=image_url,
        visual_features=[VisualFeatures.READ],
    )

    lines = []
    if result.read is not None:
        for block in result.read.blocks:
            for line in block.lines:
                lines.append(line.text)

    raw_text = "\n".join(lines)

    # Extract asset code (KT-AS-XXXX or 9-10 digit numbers)
    asset_code: Optional[str] = None
    match = re.search(r"KT-AS-\d{4}|\b\d{9,10}\b", raw_text)
    if match:
        asset_code = match.group()

    return {"raw_text": raw_text, "asset_code": asset_code}

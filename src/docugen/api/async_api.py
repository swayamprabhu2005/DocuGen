"""Asynchronous document generation and batch orchestration API for DocuGen AI."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from docugen.core.configuration import DocuGenConfig
from docugen.core.models import GenerationResult
from docugen.generation.generator import generate
from docugen.signing.digital_signature import DigitalSignatureConfig


async def generate_document_async(
    data: Any,
    template: Optional[Union[str, Path]] = None,
    document_type: Optional[str] = None,
    output: str = "pdf",
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[DocuGenConfig] = None,
    strict: Optional[bool] = None,
    dry_run: bool = False,
    digital_signature: Optional[Union[DigitalSignatureConfig, bool]] = None,
    watermark: Optional[Any] = None,
) -> GenerationResult:
    """Asynchronously generate a document in a non-blocking worker thread.

    Suitable for async frameworks such as FastAPI, Tornado, and asyncio event loops.
    """
    return await asyncio.to_thread(
        generate,
        data=data,
        template=template,
        document_type=document_type,
        output=output,
        output_path=output_path,
        config=config,
        strict=strict,
        dry_run=dry_run,
        digital_signature=digital_signature,
        watermark=watermark,
    )


async def generate_documents_batch(
    items: Sequence[Dict[str, Any]],
    max_concurrency: int = 4,
) -> List[GenerationResult]:
    """Execute high-throughput batch generation of multiple documents with bounded concurrency.

    Args:
        items: List of document request parameter dictionaries.
               Each item dictionary must provide 'data', and optionally 'template',
               'output', 'output_path', 'digital_signature', etc.
        max_concurrency: Maximum number of simultaneous generation workers.

    Returns:
        List[GenerationResult]: Ordered list of results matching the input items sequence.
    """
    semaphore = asyncio.Semaphore(max(1, max_concurrency))

    async def _worker(item: Dict[str, Any]) -> GenerationResult:
        async with semaphore:
            return await generate_document_async(
                data=item.get("data"),
                template=item.get("template"),
                document_type=item.get("document_type"),
                output=item.get("output", "pdf"),
                output_path=item.get("output_path"),
                config=item.get("config"),
                strict=item.get("strict"),
                dry_run=item.get("dry_run", False),
                digital_signature=item.get("digital_signature"),
                watermark=item.get("watermark"),
            )

    tasks = [_worker(it) for it in items]
    return await asyncio.gather(*tasks)

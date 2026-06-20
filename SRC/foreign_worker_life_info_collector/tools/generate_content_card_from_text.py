from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from foreign_worker_life_info_collector.utils.content_card_payload_generator import (
    CardPayloadRequest,
    generate_card_from_text,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a WorkConnect content card PNG from source text.")
    parser.add_argument("--input", help="Input JSON file path.")
    parser.add_argument("--template", dest="template_type", help="Template type, e.g. LIVING_IN_KOREA.")
    parser.add_argument("--text", dest="content_text", help="Source content text.")
    parser.add_argument("--source", help="Source display name.")
    parser.add_argument("--link", help="Source link.")
    parser.add_argument("--date", help="YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--category", help="Optional category for template selection.")
    parser.add_argument("--source-domain", help="Optional source_domain for template selection.")
    parser.add_argument("--output-dir", help="Output directory. Defaults to storage/generated/content_cards.")
    parser.add_argument("--endpoint", help="Override local LLaMA/Ollama endpoint.")
    parser.add_argument("--model", help="Override local LLaMA/Ollama model.")
    parser.add_argument("--timeout", type=int, help="LLaMA request timeout seconds.")
    parser.add_argument("--sample-mode", action="store_true", help="Use the template sample payload instead of calling LLaMA.")
    args = parser.parse_args(argv)

    data = load_input(args)
    request = CardPayloadRequest(
        content_text=str(data.get("content_text") or data.get("text") or ""),
        source=str(data.get("source") or ""),
        link=str(data.get("link") or data.get("source_link") or ""),
        date=str(data.get("date") or ""),
        template_type=str(data.get("template_type") or data.get("template") or ""),
        category=str(data.get("category") or ""),
        source_domain=str(data.get("source_domain") or ""),
    )
    output_dir = Path(args.output_dir) if args.output_dir else None
    result = generate_card_from_text(
        request,
        output_dir=output_dir,
        sample_mode=bool(args.sample_mode),
        endpoint=args.endpoint or "",
        model=args.model or "",
        timeout_seconds=args.timeout,
    )
    print(json.dumps(public_result(result), ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 2


def load_input(args: argparse.Namespace) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if args.input:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit("--input JSON must contain an object.")
    cli_data = {
        "template_type": args.template_type,
        "content_text": args.content_text,
        "source": args.source,
        "link": args.link,
        "date": args.date,
        "category": args.category,
        "source_domain": args.source_domain,
    }
    for key, value in cli_data.items():
        if value:
            data[key] = value
    return data


def public_result(result: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "ok",
        "status",
        "validation_status",
        "llama_status",
        "template_type",
        "source",
        "date",
        "generated_image_path",
        "generated_payload_path",
        "error_message",
    ]
    public = {key: result[key] for key in keys if key in result}
    if result.get("ok") and isinstance(result.get("payload"), dict):
        public["payload"] = result["payload"]
    return public


if __name__ == "__main__":
    raise SystemExit(main())

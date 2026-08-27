#!/usr/bin/env python3
"""Bounded OpenAlex discovery with reproducible query metadata."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


API_URL = "https://api.openalex.org/works"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--mode", choices=("keyword", "semantic"), default="keyword")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--year-from", type=int)
    parser.add_argument("--year-to", type=int)
    parser.add_argument("--open-access", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    max_limit = 50 if args.mode == "semantic" else 200
    if not 1 <= args.limit <= max_limit:
        parser.error(f"--limit must be from 1 to {max_limit} in {args.mode} mode")
    if args.year_from and args.year_to and args.year_from > args.year_to:
        parser.error("--year-from cannot be after --year-to")
    return args


def inverted_index_to_text(index: dict[str, list[int]] | None) -> str | None:
    if not index:
        return None
    positioned = [(position, word) for word, positions in index.items() for position in positions]
    positioned.sort()
    return " ".join(word for _, word in positioned)


def build_url(args: argparse.Namespace) -> str:
    params: dict[str, str] = {"per-page": str(args.limit)}
    if args.mode == "semantic":
        params["search.semantic"] = args.query
    else:
        params["search"] = args.query

    filters: list[str] = []
    if args.year_from:
        filters.append(f"from_publication_date:{args.year_from}-01-01")
    if args.year_to:
        filters.append(f"to_publication_date:{args.year_to}-12-31")
    if args.open_access:
        filters.append("is_oa:true")
    if filters:
        params["filter"] = ",".join(filters)

    key = os.getenv("OPENALEX_API_KEY")
    if key:
        params["api_key"] = key
    return f"{API_URL}?{urllib.parse.urlencode(params)}"


def request_json(url: str, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "karya-research-router/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
        except urllib.error.URLError:
            if attempt == 3:
                raise
        time.sleep(2**attempt)
    raise RuntimeError("OpenAlex request failed")


def normalize(work: dict[str, Any]) -> dict[str, Any]:
    primary = work.get("primary_location") or {}
    source = primary.get("source") or {}
    best_oa = work.get("best_oa_location") or {}
    return {
        "openalex_id": work.get("id"),
        "doi": work.get("doi"),
        "title": work.get("title"),
        "publication_year": work.get("publication_year"),
        "publication_date": work.get("publication_date"),
        "type": work.get("type"),
        "cited_by_count": work.get("cited_by_count"),
        "authors": [
            {
                "name": (authorship.get("author") or {}).get("display_name"),
                "openalex_id": (authorship.get("author") or {}).get("id"),
            }
            for authorship in work.get("authorships", [])
        ],
        "venue": source.get("display_name"),
        "landing_page_url": primary.get("landing_page_url") or best_oa.get("landing_page_url"),
        "pdf_url": best_oa.get("pdf_url"),
        "is_open_access": (work.get("open_access") or {}).get("is_oa"),
        "abstract_reconstructed": inverted_index_to_text(work.get("abstract_inverted_index")),
    }


def main() -> int:
    args = parse_args()
    url = build_url(args)
    data = request_json(url, args.timeout)
    output = {
        "schema_version": "1.0",
        "source": "OpenAlex",
        "query": {
            "text": args.query,
            "mode": args.mode,
            "limit": args.limit,
            "year_from": args.year_from,
            "year_to": args.year_to,
            "open_access": args.open_access,
        },
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "api_key_configured": bool(os.getenv("OPENALEX_API_KEY")),
        "meta": data.get("meta"),
        "results": [normalize(work) for work in data.get("results", [])],
        "limitations": [
            "OpenAlex metadata and reconstructed abstracts are discovery aids; inspect original works before substantive claims.",
            "Citation count is not a quality score.",
        ],
    }
    serialized = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(serialized, encoding="utf-8")
    else:
        sys.stdout.write(serialized)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as error:
        sys.stderr.write(f"OpenAlex request failed: {error}\n")
        raise SystemExit(1)

import argparse
import asyncio
from typing import Any

import httpx


SAMPLE_RECORDS = [
    {
        "text": "B2B fintech lead generation for SaaS companies",
        "metadata": {"source": "sample", "category": "fintech", "id": "sample-001"},
    },
    {
        "text": "Payment fraud detection platform for online transactions",
        "metadata": {"source": "sample", "category": "fintech", "id": "sample-002"},
    },
    {
        "text": "Invoice automation and accounts payable workflow software",
        "metadata": {"source": "sample", "category": "fintech", "id": "sample-003"},
    },
    {
        "text": "AI chatbot for customer support automation",
        "metadata": {"source": "sample", "category": "support", "id": "sample-004"},
    },
    {
        "text": "Helpdesk ticket routing and customer service analytics",
        "metadata": {"source": "sample", "category": "support", "id": "sample-005"},
    },
    {
        "text": "Live chat software for ecommerce support teams",
        "metadata": {"source": "sample", "category": "support", "id": "sample-006"},
    },
    {
        "text": "Real estate property listings and buyer leads",
        "metadata": {"source": "sample", "category": "real_estate", "id": "sample-007"},
    },
    {
        "text": "Commercial office rental search for growing startups",
        "metadata": {"source": "sample", "category": "real_estate", "id": "sample-008"},
    },
    {
        "text": "Mortgage prequalification leads for home buyers",
        "metadata": {"source": "sample", "category": "real_estate", "id": "sample-009"},
    },
    {
        "text": "Healthcare appointment scheduling for clinics",
        "metadata": {"source": "sample", "category": "healthcare", "id": "sample-010"},
    },
    {
        "text": "Patient reminder system for dental practices",
        "metadata": {"source": "sample", "category": "healthcare", "id": "sample-011"},
    },
    {
        "text": "Telemedicine platform for remote doctor consultations",
        "metadata": {"source": "sample", "category": "healthcare", "id": "sample-012"},
    },
    {
        "text": "Restaurant food delivery and online menu ordering",
        "metadata": {"source": "sample", "category": "restaurant", "id": "sample-013"},
    },
    {
        "text": "Table reservation system for fine dining restaurants",
        "metadata": {"source": "sample", "category": "restaurant", "id": "sample-014"},
    },
    {
        "text": "Kitchen inventory management for cafe owners",
        "metadata": {"source": "sample", "category": "restaurant", "id": "sample-015"},
    },
    {
        "text": "Online course platform for programming education",
        "metadata": {"source": "sample", "category": "education", "id": "sample-016"},
    },
    {
        "text": "Math tutoring marketplace for high school students",
        "metadata": {"source": "sample", "category": "education", "id": "sample-017"},
    },
    {
        "text": "Learning management system for corporate training",
        "metadata": {"source": "sample", "category": "education", "id": "sample-018"},
    },
    {
        "text": "Travel booking engine for hotels and flights",
        "metadata": {"source": "sample", "category": "travel", "id": "sample-019"},
    },
    {
        "text": "Vacation rental search for families near beaches",
        "metadata": {"source": "sample", "category": "travel", "id": "sample-020"},
    },
    {
        "text": "Business expense management for employee travel",
        "metadata": {"source": "sample", "category": "travel", "id": "sample-021"},
    },
    {
        "text": "Ecommerce product recommendation engine for fashion stores",
        "metadata": {"source": "sample", "category": "ecommerce", "id": "sample-022"},
    },
    {
        "text": "Shopping cart recovery email automation",
        "metadata": {"source": "sample", "category": "ecommerce", "id": "sample-023"},
    },
    {
        "text": "Inventory forecasting for online retailers",
        "metadata": {"source": "sample", "category": "ecommerce", "id": "sample-024"},
    },
    {
        "text": "Recruiting software for candidate tracking and interviews",
        "metadata": {"source": "sample", "category": "hr", "id": "sample-025"},
    },
    {
        "text": "Payroll and benefits management for small businesses",
        "metadata": {"source": "sample", "category": "hr", "id": "sample-026"},
    },
    {
        "text": "Employee engagement surveys and workplace analytics",
        "metadata": {"source": "sample", "category": "hr", "id": "sample-027"},
    },
    {
        "text": "Contract review automation for legal teams",
        "metadata": {"source": "sample", "category": "legal", "id": "sample-028"},
    },
    {
        "text": "Case management software for law firms",
        "metadata": {"source": "sample", "category": "legal", "id": "sample-029"},
    },
    {
        "text": "Compliance monitoring for financial regulations",
        "metadata": {"source": "sample", "category": "legal", "id": "sample-030"},
    },
]


async def ingest_records(api_url: str, records: list[dict[str, Any]]) -> None:
    async with httpx.AsyncClient(timeout=60) as client:
        health = await client.get(f"{api_url}/health")
        health.raise_for_status()
        print(f"Health: {health.json()}")

        stored = 0
        for record in records:
            response = await client.post(f"{api_url}/ingest", json=record)
            response.raise_for_status()
            stored += 1
            if stored % 25 == 0 or stored == len(records):
                print(f"Stored {stored}/{len(records)} records")


def load_sample_records(limit: int) -> list[dict[str, Any]]:
    return SAMPLE_RECORDS[:limit]


def load_hm_records(limit: int) -> list[dict[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit(
            "Hugging Face dataset mode requires the optional package: "
            "pip install datasets"
        ) from exc

    dataset = load_dataset("Qdrant/hm_ecommerce_products", split="train", streaming=True)
    records: list[dict[str, Any]] = []

    for row in dataset:
        text = build_hm_text(row)
        if not text:
            continue

        records.append(
            {
                "text": text,
                "metadata": {
                    "source": "Qdrant/hm_ecommerce_products",
                    "article_id": row.get("article_id"),
                    "product_code": row.get("product_code"),
                    "prod_name": row.get("prod_name"),
                    "product_type_name": row.get("product_type_name"),
                    "product_group_name": row.get("product_group_name"),
                    "colour_group_name": row.get("colour_group_name"),
                },
            }
        )

        if len(records) >= limit:
            break

    return records


def build_hm_text(row: dict[str, Any]) -> str:
    parts = [
        row.get("prod_name"),
        row.get("product_type_name"),
        row.get("product_group_name"),
        row.get("graphical_appearance_name"),
        row.get("colour_group_name"),
        row.get("detail_desc"),
    ]
    return " ".join(str(part).strip() for part in parts if part).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed semantic search records through the API.")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    parser.add_argument("--source", choices=["sample", "hm"], default="sample")
    parser.add_argument("--limit", type=int, default=30)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    if args.limit < 1:
        raise SystemExit("--limit must be at least 1")

    records = load_sample_records(args.limit) if args.source == "sample" else load_hm_records(args.limit)
    if not records:
        raise SystemExit("No records loaded.")

    await ingest_records(args.api_url.rstrip("/"), records)


if __name__ == "__main__":
    asyncio.run(main())

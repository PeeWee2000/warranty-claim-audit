"""Load synthetic claim embeddings into Qdrant.

Usage:
    python scripts/load_vectors.py [--data data/processed/synthetic_claims.json]

This script:
1. Loads the synthetic claims dataset
2. Decomposes each claim into components
3. Generates embeddings for each component
4. Creates a Qdrant collection and uploads all vectors with metadata
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "claim_components"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    parser = argparse.ArgumentParser(description="Load claim vectors into Qdrant")
    parser.add_argument("--data", default="data/processed/synthetic_claims.json")
    parser.add_argument("--qdrant-host", default="localhost")
    parser.add_argument("--qdrant-port", type=int, default=6333)
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    # Load claims
    print(f"Loading claims from {args.data}...")
    with open(args.data) as f:
        claims = json.load(f)
    print(f"Loaded {len(claims)} claims")

    # Load embedding model
    print(f"Loading embedding model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    embedding_dim = model.get_sentence_embedding_dimension()
    print(f"Embedding dimension: {embedding_dim}")

    # Connect to Qdrant
    client = QdrantClient(host=args.qdrant_host, port=args.qdrant_port)
    print(f"Connected to Qdrant at {args.qdrant_host}:{args.qdrant_port}")

    # Recreate collection
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection: {COLLECTION_NAME}")

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=embedding_dim,
            distance=Distance.COSINE,
        ),
    )
    print(f"Created collection: {COLLECTION_NAME}")

    # Process claims and build component vectors
    print("\nProcessing claims and generating embeddings...")
    points: list[PointStruct] = []
    point_id = 0

    # Collect all texts to embed in batches
    texts_to_embed: list[str] = []
    metadata_list: list[dict] = []

    for claim_idx, claim in enumerate(claims):
        text = claim.get("text", "")
        label = claim.get("label", "unknown")
        fraud_type = claim.get("fraud_type")
        scenario = claim.get("scenario", "unknown")

        # Extract component texts from the claim
        components = _extract_component_texts(text)

        for comp_name, comp_text in components.items():
            texts_to_embed.append(comp_text)
            metadata_list.append({
                "claim_idx": claim_idx,
                "component": comp_name,
                "label": label,
                "fraud_type": fraud_type or "",
                "scenario": scenario,
                "text_preview": comp_text[:200],
            })

    print(f"Total component vectors to embed: {len(texts_to_embed)}")

    # Batch encode
    print("Generating embeddings (this may take a minute)...")
    all_embeddings = model.encode(
        texts_to_embed,
        batch_size=args.batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    # Build Qdrant points
    for i, (embedding, meta) in enumerate(zip(all_embeddings, metadata_list)):
        points.append(PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload=meta,
        ))

    # Upload in batches
    batch_size = 100
    print(f"\nUploading {len(points)} vectors to Qdrant...")
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch,
        )
        if (i // batch_size) % 10 == 0:
            print(f"  Uploaded {min(i + batch_size, len(points))}/{len(points)} vectors")

    # Verify
    info = client.get_collection(COLLECTION_NAME)
    print(f"\nCollection info:")
    print(f"  Vectors: {info.points_count}")
    print(f"  Status: {info.status}")
    print("\nDone! Vectors loaded into Qdrant.")


def _extract_component_texts(text: str) -> dict[str, str]:
    """Extract component texts from a claim narrative for embedding.

    Uses simple heuristics to identify sections of the claim text
    that correspond to different components.
    """
    components = {}
    sentences = [s.strip() for s in text.split(".") if s.strip()]

    symptom_parts = []
    diagnosis_parts = []
    parts_parts = []
    labor_parts = []

    for sentence in sentences:
        lower = sentence.lower()
        if any(kw in lower for kw in ["customer states", "customer reports", "complaint"]):
            symptom_parts.append(sentence)
        elif any(kw in lower for kw in ["diagnosis", "found", "confirmed", "tested", "fault", "dtc"]):
            diagnosis_parts.append(sentence)
        elif any(kw in lower for kw in ["replaced", "parts total", "also replaced"]):
            parts_parts.append(sentence)
        elif any(kw in lower for kw in ["labor", "hours", "book time"]):
            labor_parts.append(sentence)

    if symptom_parts:
        components["symptom"] = ". ".join(symptom_parts)
    if diagnosis_parts:
        components["diagnosis"] = ". ".join(diagnosis_parts)
    if parts_parts:
        components["parts"] = ". ".join(parts_parts)
    if labor_parts:
        components["labor"] = ". ".join(labor_parts)

    # Always include full verbatim
    components["verbatim"] = text

    return components


if __name__ == "__main__":
    main()

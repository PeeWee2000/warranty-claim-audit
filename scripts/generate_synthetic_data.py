"""Script to generate and save a synthetic training dataset.

Usage:
    python scripts/generate_synthetic_data.py [--n-legitimate 700] [--n-fraudulent 300] [--seed 42]
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path so we can import the ml package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.synthetic_data.generator import generate_dataset
from ml.synthetic_data.validator import validate_claim


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic warranty claims")
    parser.add_argument("--n-legitimate", type=int, default=700)
    parser.add_argument("--n-fraudulent", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/synthetic_claims.json",
    )
    args = parser.parse_args()

    print(f"Generating {args.n_legitimate} legitimate + {args.n_fraudulent} fraudulent claims...")
    claims = generate_dataset(
        n_legitimate=args.n_legitimate,
        n_fraudulent=args.n_fraudulent,
        seed=args.seed,
    )

    # Validate all claims
    invalid_count = 0
    for i, claim in enumerate(claims):
        result = validate_claim(claim)
        if not result.valid:
            invalid_count += 1
            print(f"  Claim {i} invalid: {result.errors}")

    print(f"Generated {len(claims)} claims ({invalid_count} invalid)")

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(claims, f, indent=2)

    print(f"Saved to {output_path}")

    # Print summary
    labels = {}
    fraud_types = {}
    for c in claims:
        labels[c["label"]] = labels.get(c["label"], 0) + 1
        if c.get("fraud_type"):
            fraud_types[c["fraud_type"]] = fraud_types.get(c["fraud_type"], 0) + 1

    print(f"\nLabel distribution: {labels}")
    if fraud_types:
        print(f"Fraud types: {fraud_types}")


if __name__ == "__main__":
    main()

import json
import gzip
import pickle
import argparse
import csv
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scorer import compute_final_score
from reasoning import generate_reasoning


def resolve_candidates_path(path=None):
    if path:
        return path

    for candidate in (
        "./candidates.jsonl",
        "./candidates.jsonl.gz",
        "candidates.jsonl",
        "candidates.jsonl.gz",
    ):
        if os.path.exists(candidate):
            return candidate

    return None


def resolve_features_path(path=None):
    if path:
        return path

    for feature_file in ("./candidate_features.pkl", "candidate_features.pkl"):
        if os.path.exists(feature_file):
            return feature_file

    return None


def load_candidates(path):
    if path.endswith(".gz"):
        with gzip.open(path, "rt") as f:
            return [json.loads(line) for line in f if line.strip()]
    else:
        with open(path, "r") as f:
            return [json.loads(line) for line in f if line.strip()]


def load_features(pkl_path):
    with open(pkl_path, "rb") as f:
        return pickle.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Rank candidates for Redrob Senior AI Engineer role"
    )
    parser.add_argument(
        "--candidates", default=None,
        help="Path to candidates.jsonl or candidates.jsonl.gz (auto-detected if omitted)"
    )
    parser.add_argument(
        "--out", default="submission.csv",
        help="Output CSV path (default: submission.csv)"
    )
    parser.add_argument(
        "--features", default=None,
        help="Path to precomputed features pickle (auto-detected if omitted)"
    )
    args = parser.parse_args()

    candidate_path = resolve_candidates_path(args.candidates)
    if not candidate_path:
        raise SystemExit(
            "No candidates file found. Provide --candidates or place candidates.jsonl/candidates.jsonl.gz in the project directory."
        )

    features_path = resolve_features_path(args.features)
    if not features_path:
        raise SystemExit(
            "No precomputed features file found. Run precompute.py first to create candidate_features.pkl."
        )

    print(f"Loading candidates from {candidate_path}...")
    candidates = load_candidates(candidate_path)
    print(f"Loaded {len(candidates):,} candidates")

    print(f"Loading precomputed features from {features_path}...")
    features      = load_features(features_path)
    idf_map       = features["idf_map"]
    title_idf_map = features["title_idf_map"]

    # ── Score all candidates ──────────────────────────────────────
    print("Scoring candidates...")
    start = datetime.now()

    results = []
    for candidate in candidates:
        result = compute_final_score(candidate, idf_map, title_idf_map)
        results.append({
            "candidate_id": candidate["candidate_id"],
            "final_score":  result["final_score"],
            "_candidate":   candidate,
            "_result":      result
        })

    elapsed = (datetime.now() - start).total_seconds()
    print(f"Scored {len(results):,} candidates in {elapsed:.1f}s")

    # ── Sort and take top 100 ─────────────────────────────────────
    results.sort(key=lambda x: (x["final_score"], -ord(x["candidate_id"][-1])), reverse=True)
    top_100 = results[:100]

    # ── Generate reasoning ────────────────────────────────────────
    print("Generating reasoning for top 100...")
    rows = []
    for rank, r in enumerate(top_100, start=1):
        reasoning = generate_reasoning(r["_candidate"], r["_result"])
        rows.append({
            "candidate_id": r["candidate_id"],
            "rank":         rank,
            "score":        r["final_score"],
            "reasoning":    reasoning
        })

    # Tie-breaking: equal scores → candidate_id ascending (per spec)
    rows.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    for i, row in enumerate(rows):
        row["rank"] = i + 1

    # ── Write CSV ─────────────────────────────────────────────────
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Writing submission to {out_path}...")
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["candidate_id", "rank", "score", "reasoning"]
        )
        writer.writeheader()
        writer.writerows(rows)

    # ── Summary ───────────────────────────────────────────────────
    print()
    print("=" * 50)
    print("SUBMISSION SUMMARY")
    print("=" * 50)
    print(f"Total candidates scored : {len(results):,}")
    print(f"Top score               : {rows[0]['score']}")
    print(f"Rank 100 score          : {rows[-1]['score']}")
    print(f"Output file             : {args.out}")
    print()
    print("Top 5 candidates:")
    for row in rows[:5]:
        print(f"  Rank {row['rank']}: {row['candidate_id']} (score={row['score']})")
    print()
    print("Run validate_submission.py to verify format before uploading.")


if __name__ == "__main__":
    main()
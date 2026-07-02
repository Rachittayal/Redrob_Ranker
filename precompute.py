import json
import gzip
import pickle
import argparse
import os
from pathlib import Path
import numpy as np
from collections import defaultdict


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


def load_candidates(path):
    if path.endswith(".gz"):
        with gzip.open(path, "rt") as f:
            return [json.loads(line) for line in f if line.strip()]
    else:
        with open(path, "r") as f:
            return [json.loads(line) for line in f if line.strip()]


def build_skill_freq_map(candidates):
    freq = defaultdict(int)
    for c in candidates:
        for skill in c.get("skills", []):
            freq[skill["name"].lower()] += 1
    return dict(freq)


def build_idf_map(freq_map, N):
    return {skill: np.log(N / (1 + count)) for skill, count in freq_map.items()}


def build_title_freq_map(candidates):
    freq = defaultdict(int)
    seen = set()
    for c in candidates:
        seen.clear()
        for role in c.get("career_history", []):
            t = role.get("title", "")
            if t and t not in seen:
                freq[t] += 1
                seen.add(t)
    return dict(freq)


def build_title_idf_map(title_freq_map, N):
    return {title: np.log10(N / (1 + count)) for title, count in title_freq_map.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default=None, help="Path to candidates.jsonl or .jsonl.gz")
    parser.add_argument("--out", default="candidate_features.pkl", help="Output pickle path")
    args = parser.parse_args()

    candidate_path = resolve_candidates_path(args.candidates)
    if not candidate_path:
        raise SystemExit(
            "No candidates file found. Provide --candidates or place candidates.jsonl/candidates.jsonl.gz in the project directory."
        )

    print(f"Loading candidates from {candidate_path}...")
    candidates = load_candidates(candidate_path)
    N = len(candidates)
    print(f"Loaded {N:,} candidates")

    print("Building skill frequency map...")
    skill_freq_map = build_skill_freq_map(candidates)

    print("Building IDF map...")
    idf_map = build_idf_map(skill_freq_map, N)

    print("Building title frequency map...")
    title_freq_map = build_title_freq_map(candidates)

    print("Building title IDF map...")
    title_idf_map = build_title_idf_map(title_freq_map, N)

    features = {
        "idf_map":       idf_map,
        "title_idf_map": title_idf_map,
        "N":             N
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving features to {out_path}...")
    with out_path.open("wb") as f:
        pickle.dump(features, f)

    print(f"Done. Precomputed {len(idf_map)} skill IDFs, {len(title_idf_map)} title IDFs.")


if __name__ == "__main__":
    main()


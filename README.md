# Redrob Candidate Ranker

**Team:** `<TEAM_NAME>`
**Challenge:** Intelligent Candidate Discovery & Ranking Challenge — Redrob Hackathon v4
**Role ranked against:** Senior AI Engineer — Founding Team (Redrob AI)

A rule-based, transparent candidate ranking system that scores all 100,000 candidates
in `candidates.jsonl` against a single fixed job description and outputs the top 100,
with per-candidate reasoning grounded entirely in real profile fields.

---

## 1. Why this architecture

The job description is fixed for the entire competition — there is exactly one JD to
rank against, known in advance. Rather than building a general-purpose JD parser (an
NLP problem that doesn't exist here), the JD's requirements are hand-encoded once into
structured, inspectable config (`jd_config.py`). This is more accurate than an automated
parse would be, and every scoring weight can be traced directly back to a specific
sentence in the JD.

Given the compute constraints — **≤5 min wall-clock, ≤16GB RAM, CPU-only, no network**
— the system is split into two phases:

- **Offline pre-computation** (`precompute.py`): builds skill/title frequency and IDF
  maps from the full candidate pool. Not time-boxed by the submission rules; only needs
  to run once.
- **Runtime ranking** (`rank.py`): loads the pre-computed artifacts, scores all 100,000
  candidates, and writes the top 100 to `submission.csv`. This is the step that is
  reproduced under the 5-minute budget at Stage 3.

Scoring is a transparent weighted combination of explicit, hand-set feature weights —
not a learned/black-box model. This is a deliberate choice, not a shortcut: there is no
ground-truth relevance data available during the competition (no live leaderboard, no
per-submission feedback) to train a ranker against, so a learned model would either be
untrained or trained on self-generated pseudo-labels, which is circular. Hand-set,
JD-traceable weights are the more defensible and more explainable choice given this
constraint, and directly serve Stage 4's requirement that reasoning connect to specific,
real evidence rather than an opaque score.

---

## 2. Repository structure

```
redrob_ranker/
├── jd_config.py                    # Hand-encoded JD requirements (must-haves, gates, weights)
├── precompute.py                   # Offline: builds skill/title IDF + frequency maps
├── scorer.py                       # Per-candidate component scoring functions
├── honeypot.py                     # Structural consistency / honeypot detection
├── reasoning.py                    # Generates grounded 1-2 sentence reasoning per candidate
├── rank.py                         # Runtime: loads artifacts, scores, ranks, writes CSV
├── validate_submission.py          # Format validator (provided by organizers)
├── candidate_features.pkl          # Pre-computed artifact (output of precompute.py)
├── submission.csv                  # Last generated submission (for reference — see §5)
├── submission_metadata.yaml        # Filled-in portal metadata (mirrors template)
├── submission_metadata_template.yaml
├── pyproject.toml / uv.lock        # Dependency management (uv)
├── requirements.txt                # Dependency list (pip fallback)
└── README.md
```

> **Note:** `candidates.jsonl` (the 100K candidate pool) is not committed to this repo
> — at ~465MB uncompressed it exceeds GitHub's file-size limits and is already provided
> separately by the organizers. Place it in the repo root before running the commands
> below.

---

## 3. Setup

```bash
git clone https://github.com/<USERNAME>/<REPO>.git
cd redrob_ranker

# Using uv (recommended)
uv sync

# Or using pip
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Place the provided `candidates.jsonl` in the repo root.

---

## 4. Reproducing the submission

Run in order — **`precompute.py` must run before `rank.py`**, since `rank.py` depends
on the artifact it produces:

```bash
# Step 1 — offline pre-computation (not time-constrained)
uv run precompute.py --candidates ./candidates.jsonl --out ./candidate_features.pkl

# Step 2 — runtime ranking (must complete within 5 min / 16GB / CPU-only / no network)
uv run rank.py --candidates ./candidates.jsonl --features ./candidate_features.pkl --out ./submission.csv
```

Example output from `rank.py`:

```
Loading candidates from ./candidates.jsonl...
Loaded 100,000 candidates
Loading precomputed features from ./candidate_features.pkl...
Scoring candidates...
Scored 100,000 candidates in 46.3s
Generating reasoning for top 100...
Writing submission to submission.csv...
==================================================
SUBMISSION SUMMARY
==================================================
Total candidates scored : 100,000
Top score                : 0.9411
Rank 100 score            : 0.8241
Output file               : submission.csv
```

Scoring 100K candidates completes in well under a minute on a standard laptop CPU —
comfortably inside the 5-minute budget, with margin for the reproduction environment
being slower than local hardware.

### Validate before submitting

```bash
uv run validate_submission.py submission.csv
```

This checks the exact rules in Section 3 of `submission_spec.md` (row count, rank
uniqueness, score monotonicity, tie-break ordering, header format) before upload.

---

## 5. Scoring methodology

Each candidate receives a `final_score` composed of five weighted components, applied
only after a hard honeypot/consistency gate:

| Component      | Weight | What it captures |
|-----------------|:------:|-------------------|
| `career_score`      | 0.35 | Evidence of *shipping* ranking/search/recommendation systems to production, weighted by recency; derived from career_history descriptions, not job titles alone |
| `skill_score`        | 0.25 | JD-relevant skills, tiered by relevance (retrieval/IR core vs. general ML vs. adjacent), weighted by proficiency, endorsement count, and duration — corroborated against platform-verified `skill_assessment_scores` where available |
| `experience_score`  | 0.15 | Years-of-experience fit against the JD's stated 5–9 year range, combined with tenure stability (penalizing rapid job-hopping, per the JD's explicit "title-chaser" disqualifier) |
| `availability_score` | 0.15 | Platform activity recency, recruiter response rate, notice period, and open-to-work status — modeled as a bounded modifier, not a multiplier that can zero out an otherwise strong candidate |
| `trust_score`         | 0.10 | Profile completeness, verification status, and GitHub activity as a baseline credibility signal |

**Hard gates applied before weighting** (candidates failing these are scored 0 /
heavily suppressed regardless of other components):

- Confirmed honeypot patterns (see §6)
- Career history entirely within pure-consulting/services companies (TCS, Infosys,
  Wipro, Accenture, Cognizant, Capgemini, etc.) with no product-company experience —
  per the JD's explicit disqualifier
- CV/speech/robotics-dominant skill profile with no NLP/IR exposure — per the JD's
  explicit disqualifier

All weights and thresholds are defined in `jd_config.py` and traceable to specific
statements in `job_description.md`.

---

## 6. Honeypot & trap handling

The dataset contains ~80 honeypot candidates with structurally impossible profiles.
`honeypot.py` flags candidates via deterministic, threshold-validated checks:

- 3+ skills marked `advanced`/`expert` proficiency with `duration_months == 0`
  (impossible to have expert-level proficiency with zero time spent)
- Current role's `duration_months` alone exceeding the candidate's total stated
  `years_of_experience`

Both thresholds were validated by sensitivity sweeps across the full 100K pool (see
commit history) to confirm they isolate genuinely impossible profiles rather than
legitimate edge cases. Flagged candidates are excluded from the ranking outright.

Additional trap resistance (keyword-stuffing, title/skill mismatch) is handled
implicitly through the scoring design itself: `career_score` weights career-history
*description* text far more heavily than `skills[]` list contents, so a profile with
an AI-heavy skills list under an unrelated job title does not automatically score well.

---

## 7. Reasoning generation

Reasoning strings in `submission.csv` are generated by `reasoning.py` using templated
sentence construction over the *actual computed score components and profile fields*
for that candidate — never freely generated text. Every claim (named skills, named
employers, signal values) is pulled directly from data that exists in the candidate's
profile, and genuine concerns (long notice period, low response rate, inactivity,
consulting-only background) are surfaced rather than omitted, per Stage 4's "honest
concerns" and "no hallucination" checks.

---

## 8. Compute environment

| | |
|---|---|
| Platform | `<e.g. MacBook Pro M2 / Windows 11 laptop>` |
| CPU cores | `<N>` |
| RAM | `<N> GB` |
| Python | `<3.11.x>` |
| GPU used for inference | No |
| Network during ranking | No |
| Pre-computation required | Yes — `precompute.py`, ~`<N>` seconds, not counted against the 5-minute ranking budget |

Full details in `submission_metadata.yaml`.

---

## 9. AI tools disclosure

AI tools used during development are declared honestly in `submission_metadata.yaml`.
No candidate data was sent to any external LLM API — all development-time AI assistance
was used for code review, architecture discussion, and debugging, not for the ranking
logic itself, which runs entirely offline per the compute constraints.

---

## 10. Known limitations

- Company and title relevance classifications (`jd_config.py`) are derived from the
  closed set of ~63 companies and ~48 titles present in this specific dataset; they are
  not a general-purpose classifier and would need re-deriving for a different candidate
  pool.
- `skill_assessment_scores` (platform-verified skill tests) are sparse (~0.3–1.3%
  coverage per skill) and are used as a corroboration signal where present rather than
  a primary feature, since most candidates have no assessment data to draw on.
- Scoring weights are hand-set and JD-traceable rather than learned, by design (see §1)
  — this trades potential predictive accuracy for transparency and defensibility, which
  is the appropriate trade-off given no labeled relevance data is available during the
  competition window.
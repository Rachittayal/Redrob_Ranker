

import numpy as np
import math
from datetime import datetime

from jd_config import (
    TIER_A, TIER_B, TIER_C, CV_SPEECH,
    TIER_WEIGHT, SKILL_NORMALIZATION,
    COMPANY_CLASSIFICATION,
    HIGH_FIT_TITLES, GOOD_FIT_TITLES, ADJACENT_TITLES,
    OWNERSHIP_VERBS, SYSTEM_TYPES_SAFE, SYSTEM_PHRASES_AMBIGUOUS,
    PRODUCTION_SIGNALS, EVALUATION_SIGNALS,
    WEIGHTS,
    PEAK_LOW, PEAK_HIGH, BUFFER_LOW, BUFFER_HIGH,
    TENURE_MIDPOINT, TENURE_STEEPNESS
)
from honeypot import is_honeypot

TODAY_STR = "2026-06-30"


def get_tier(skill_name):
    name = skill_name.lower().strip()
    name = SKILL_NORMALIZATION.get(name, name)
    if name in TIER_A:    return "tier_a"
    if name in TIER_B:    return "tier_b"
    if name in TIER_C:    return "tier_c"
    if name in CV_SPEECH: return "cv_speech"
    return "irrelevant"


def get_idf(skill_name, idf_map, N=100_000):
    name = skill_name.lower().strip()
    name = SKILL_NORMALIZATION.get(name, name)
    return idf_map.get(name, np.log(N / 2))


def compute_depth_factor(skill):
    
    proficiency_map = {
        "beginner": 0.25, "intermediate": 0.50,
        "advanced": 0.75, "expert": 1.00
    }
    duration     = skill.get("duration_months", 0)
    proficiency  = skill.get("proficiency", "beginner")
    endorsements = skill.get("endorsements", 0)

    if duration == 0 and proficiency in ("advanced", "expert"):
        return 0.0

    prof_score = proficiency_map.get(proficiency, 0.25)
    duration_factor = min(np.log1p(duration) / np.log1p(33), 1.15)
    endorsement_factor = np.log1p(endorsements) / np.log1p(100)

    return round(min(prof_score * duration_factor * endorsement_factor, 1.0),4)


def score_skills(candidate_skills, idf_map):
    
    total     = 0.0
    cv_count  = 0
    rel_count = 0
    top       = []

    for skill in candidate_skills:
        tier   = get_tier(skill["name"])
        weight = TIER_WEIGHT[tier]
        idf    = get_idf(skill["name"], idf_map)
        depth  = compute_depth_factor(skill)

        contribution = weight * idf * depth
        total       += contribution

        if tier == "cv_speech":
            cv_count += 1
        if tier in ("tier_a", "tier_b") and contribution > 0:
            rel_count += 1
            top.append((skill["name"], tier, round(contribution, 3)))

    total_ai    = cv_count + rel_count
    cv_dominant = (
        cv_count >= 3
        and total_ai > 0
        and (cv_count / total_ai) > 0.70
        and rel_count < 2
    )

    skill_score = min(total / 12.0, 1.0)
    top.sort(key=lambda x: x[2], reverse=True)

    return {
        "skill_score": round(skill_score, 4),
        "cv_dominant": cv_dominant,
        "rel_count":   rel_count,
        "cv_count":    cv_count,
        "top_skills":  top[:5]
    }


def classify_company(company_name):
    return COMPANY_CLASSIFICATION.get(company_name, ("unknown", 0.50))


def score_title(title, title_idf_map):
    t      = title.lower().strip()
    if t in HIGH_FIT_TITLES:   domain = 1.0
    elif t in GOOD_FIT_TITLES: domain = 0.70
    elif t in ADJACENT_TITLES: domain = 0.40
    else:                      domain = 0.10

    idf = title_idf_map.get(title, np.log10(100_000 / 2))
    idf_bonus = min(2.0 * idf / 10.0, 0.50) if domain >= 0.40 else 0.0
    return round(min(domain + idf_bonus, 1.0), 4)


def has_system_signal(description):
    
    text  = description.lower()
    words = set(text.split())

    if words & SYSTEM_TYPES_SAFE:
        return True
    for phrase in SYSTEM_PHRASES_AMBIGUOUS:
        if phrase in text:
            return True
    return False


def score_description(description):
    
    if not description:
        return 0.0

    words = set(description.lower().split())
    text  = description.lower()

    has_ownership  = bool(words & OWNERSHIP_VERBS)
    has_system     = has_system_signal(description)
    has_production = bool(words & PRODUCTION_SIGNALS)
    has_evaluation = (
        bool(words & EVALUATION_SIGNALS)
        or "a/b" in text or "ndcg" in text
        or "mrr" in text or "map@" in text
    )

    if has_ownership and has_system and has_production: base = 1.0
    elif has_ownership and has_system:                  base = 0.70
    elif has_system and has_production:                 base = 0.50
    elif has_system:                                    base = 0.30
    else:                                               base = 0.0

    return round(min(base + (0.20 if has_evaluation else 0.0), 1.0), 4)


def score_career(career_history, title_idf_map):
    
    if not career_history:
        return {
            "career_score": 0.0,
            "consulting_only": False,
            "best_description_score": 0.0
        }

    recency_weights = [1.0, 0.7, 0.5, 0.4, 0.3]
    role_scores     = []
    company_scores  = []
    best_desc_score = 0.0

    for idx, role in enumerate(career_history):
        w = recency_weights[idx] if idx < len(recency_weights) else 0.2

        _, company_sc = classify_company(role.get("company", ""))
        title_sc = score_title(role.get("title", ""), title_idf_map)
        desc_sc  = score_description(role.get("description", ""))

        best_desc_score = max(best_desc_score, desc_sc)
        role_sc = (company_sc * 0.20) + (title_sc * 0.30) + (desc_sc * 0.50)
        role_scores.append(w * role_sc)
        company_scores.append(company_sc)

    raw          = sum(role_scores)
    desc_bonus   = best_desc_score * 0.3
    career_score = min((raw + desc_bonus) / 2.5, 1.0)

    consulting_only = all(sc <= 0.25 for sc in company_scores)
    if consulting_only:
        career_score *= 0.5

    return {
        "career_score":           round(career_score, 4),
        "consulting_only":        consulting_only,
        "best_description_score": round(best_desc_score, 4)
    }


def score_years_experience(years):
    
    if PEAK_LOW <= years <= PEAK_HIGH:
        return 1.0
    elif years < PEAK_LOW:
        return round(max(0.0, 1 - (PEAK_LOW - years) / BUFFER_LOW), 4)
    else:
        return round(max(0.0, 1 - (years - PEAK_HIGH) / BUFFER_HIGH), 4)


def tenure_score_fn(avg_tenure_months):
    
    return round(
        1 / (1 + math.exp(-TENURE_STEEPNESS * (avg_tenure_months - TENURE_MIDPOINT))),4)


def score_tenure_stability(career_history):
    if not career_history:
        return 1.0
    durations = [r.get("duration_months", 0) for r in career_history if r.get("duration_months", 0) > 0]
    if not durations:
        return 1.0
    weights      = [0.8 ** i for i in range(len(durations))]
    weighted_avg = sum(d * w for d, w in zip(durations, weights)) / sum(weights)
    return tenure_score_fn(weighted_avg)


def score_experience(profile_years, career_history):
    years_sc = score_years_experience(profile_years)
    ten_sc   = score_tenure_stability(career_history)
    return {
        "experience_score": round((years_sc * 0.6) + (ten_sc * 0.4), 4),
        "years_score":      years_sc,
        "tenure_score":     ten_sc
    }


def score_notice_period(notice_days):
    if notice_days <= 30:
        return 1.0
    excess = min(notice_days - 30, 150)
    return round(max(0.3, 1.0 - (excess / 150) * 0.7), 4)


def score_activity(last_active_date, today_str=TODAY_STR):
    today         = datetime.strptime(today_str, "%Y-%m-%d")
    last_active   = datetime.strptime(last_active_date, "%Y-%m-%d")
    days_inactive = (today - last_active).days
    if days_inactive <= 7:
        return 1.0
    elif days_inactive <= 180:
        return round(max(0.3, 1.0 - (days_inactive - 7) / 173 * 0.7), 4)
    else:
        excess = min(days_inactive - 180, 180)
        return round(max(0.1, 0.3 - (excess / 180) * 0.2), 4)


def score_response_rate(rate):
    return round(rate ** 0.7, 4)


def score_availability(redrob_signals, today_str=TODAY_STR):
    activity_sc = score_activity(redrob_signals["last_active_date"], today_str)
    response_sc = score_response_rate(redrob_signals["recruiter_response_rate"])
    notice_sc   = score_notice_period(redrob_signals["notice_period_days"])
    open_sc     = 1.0 if redrob_signals["open_to_work_flag"] else 0.5

    return {
        "availability_score": round(
            (activity_sc * 0.35) + (response_sc * 0.30) +
            (notice_sc   * 0.25) + (open_sc     * 0.10), 4
        ),
        "activity_score":  activity_sc,
        "response_score":  response_sc,
        "notice_score":    notice_sc,
        "open_score":      open_sc
    }



def score_trust(redrob_signals):
    completeness    = redrob_signals["profile_completeness_score"] / 100
    verif_count     = sum([
        redrob_signals["verified_email"],
        redrob_signals["verified_phone"],
        redrob_signals["linkedin_connected"]
    ])
    verification_sc = verif_count / 3
    gh              = redrob_signals["github_activity_score"]
    github_sc       = 0.5 if gh == -1 else gh / 100

    return {
        "trust_score":     round((completeness * 0.40) + (verification_sc * 0.30) + (github_sc * 0.30), 4),
        "completeness_sc": round(completeness, 4),
        "verification_sc": round(verification_sc, 4),
        "github_sc":       round(github_sc, 4)
    }

def compute_final_score(candidate, idf_map, title_idf_map):
    
    if is_honeypot(candidate):
        return {
            "final_score": 0.0, "skill_score": 0.0,
            "career_score": 0.0, "experience_score": 0.0,
            "availability_score": 0.0, "trust_score": 0.0,
            "cv_speech_dominant": False, "consulting_only": False,
            "is_honeypot": True, "top_skills": []
        }

    sk = score_skills(candidate["skills"], idf_map)
    ca = score_career(candidate["career_history"], title_idf_map)
    ex = score_experience(
        candidate["profile"]["years_of_experience"],
        candidate["career_history"]
    )
    av = score_availability(candidate["redrob_signals"])
    tr = score_trust(candidate["redrob_signals"])

    final = round(
        ca["career_score"]       * WEIGHTS["career"]       +
        sk["skill_score"]        * WEIGHTS["skill"]        +
        ex["experience_score"]   * WEIGHTS["experience"]   +
        av["availability_score"] * WEIGHTS["availability"] +
        tr["trust_score"]        * WEIGHTS["trust"],
        4
    )

    return {
        "final_score":        final,
        "skill_score":         sk["skill_score"],
        "career_score":         ca["career_score"],
        "experience_score":     ex["experience_score"],
        "availability_score":   av["availability_score"],
        "trust_score":          tr["trust_score"],
        "cv_speech_dominant":   sk["cv_dominant"],
        "consulting_only":      ca["consulting_only"],
        "is_honeypot":          False,
        "top_skills":           sk["top_skills"]
    }


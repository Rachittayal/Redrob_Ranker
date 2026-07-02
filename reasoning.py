

from datetime import datetime
from scorer import score_description, classify_company

TODAY_STR = "2026-06-30"


def generate_reasoning(candidate, score_result):
    
    profile = candidate["profile"]
    title   = profile["current_title"]
    yoe     = profile["years_of_experience"]
    sig     = candidate["redrob_signals"]

    top_skills_named = [s[0] for s in score_result["top_skills"][:2]]

    best_role    = None
    best_desc_sc = -1
    for role in candidate["career_history"]:
        sc = score_description(role.get("description", ""))
        if sc > best_desc_sc:
            best_desc_sc = sc
            best_role    = role

    concerns = []

    if sig["notice_period_days"] > 60:
        concerns.append(f"{sig['notice_period_days']}-day notice period")

    if not sig["open_to_work_flag"]:
        concerns.append("not marked open to work")

    if sig["recruiter_response_rate"] < 0.20:
        concerns.append(
            f"low recruiter response rate ({sig['recruiter_response_rate']:.0%})"
        )

    if score_result["consulting_only"]:
        concerns.append("career entirely at consulting firms")

    if score_result["cv_speech_dominant"]:
        concerns.append(
            "primary expertise in computer vision/speech, not retrieval/NLP"
        )

    today         = datetime.strptime(TODAY_STR, "%Y-%m-%d")
    last_active   = datetime.strptime(sig["last_active_date"], "%Y-%m-%d")
    days_inactive = (today - last_active).days
    if days_inactive > 90:
        concerns.append(f"inactive on platform for {days_inactive} days")

    if top_skills_named and best_desc_sc >= 0.5:
        domain = "search/retrieval" if best_desc_sc >= 0.7 else "related"
        s1 = (
            f"{title} with {yoe} years experience; has direct evidence of "
            f"shipping a {domain} system at {best_role['company']}, "
            f"with strong skills in {', '.join(top_skills_named)}."
        )
    elif top_skills_named:
        s1 = (
            f"{title} with {yoe} years experience; shows relevant skills in "
            f"{', '.join(top_skills_named)}, though career history shows "
            f"limited direct evidence of shipped retrieval/ranking systems."
        )
    elif best_desc_sc >= 0.5:
        s1 = (
            f"{title} with {yoe} years experience; career history shows "
            f"evidence of relevant systems work at {best_role['company']}, "
            f"though skill profile is thin on named AI/ML tools."
        )
    else:
        s1 = (
            f"{title} with {yoe} years experience; limited overlap with "
            f"the role\'s core requirements in both skills and career history."
        )

    if concerns:
        s2 = f"Concerns: {'; '.join(concerns[:2])}."
    else:
        s2 = (
            f"Active on platform, open to work, "
            f"response rate {sig['recruiter_response_rate']:.0%}."
        )

    return f"{s1} {s2}"


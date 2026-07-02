def is_honeypot(candidate):
    
    yoe = candidate["profile"]["years_of_experience"]

    zero_dur_expert = sum(
        1 for s in candidate["skills"]
        if s.get("duration_months", 1) == 0
        and s.get("proficiency") in ("advanced", "expert")
    )
    if zero_dur_expert >= 3:
        return True

    
    for role in candidate["career_history"]:
        if role.get("is_current"):
            role_years = role.get("duration_months", 0) / 12
            if role_years > yoe + 0.5:
                return True
            break

    return False

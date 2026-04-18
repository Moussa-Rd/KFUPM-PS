from utils.helpers import safe_split, matches_rule, safe_lower


def check_permit_eligibility(user_permit, allowed_permits):
    """
    Check whether the user's permit type is allowed in the parking lot.
    """
    permits_list = safe_split(allowed_permits)
    return matches_rule(user_permit, permits_list)


def check_gender_eligibility(user_gender, gender_access):
    """
    Check whether the user's gender is allowed in the parking lot.
    """
    gender_list = safe_split(gender_access)
    return matches_rule(user_gender, gender_list)


def check_residency_eligibility(user_residency, allowed_residency):
    """
    Check whether the user's residency matches the lot rules.
    """
    residency_list = safe_split(allowed_residency)
    return matches_rule(user_residency, residency_list)


def check_category_eligibility(user_permit, lot_category):
    """
    Check whether the lot category is suitable for the user type.
    This is useful for KFUPM-specific categories such as:
    student, non_resident, resident, visitor, staff, faculty
    """
    categories_list = safe_split(lot_category)

    if not categories_list:
        return True

    return matches_rule(user_permit, categories_list)


def _is_time_in_range(current_time, start_time, end_time):
    """
    Compare simple HH:MM time strings.
    """
    return start_time <= current_time <= end_time


def check_time_eligibility(current_time, time_rules):
    """
    Time rule checker.

    Supported examples:
    - "all"
    - "07:00-17:00"
    - "07:00-12:00,13:00-17:00"
    """
    rule = safe_lower(time_rules)
    current_time = safe_lower(current_time)

    if rule in ["all", "", "none"]:
        return True

    try:
        time_ranges = [r.strip() for r in rule.split(",") if r.strip()]

        for time_range in time_ranges:
            start_time, end_time = [x.strip() for x in time_range.split("-")]
            if _is_time_in_range(current_time, start_time, end_time):
                return True

        return False

    except Exception:
        return False


def check_restricted_status(lot_row):
    """
    Optional restriction flag for special lots.
    If a lot is marked as restricted, treat it as not eligible
    unless your project later adds override logic.
    """
    restricted_value = safe_lower(lot_row.get("restricted", "false"))
    return restricted_value not in ["true", "yes", "1"]


def is_lot_eligible(user_profile, lot_row):
    """
    Full eligibility check for a parking lot.

    user_profile example:
    {
        "permit_type": "student",
        "gender": "male",
        "residency": "non_resident",
        "arrival_time": "08:30"
    }
    """
    permit_ok = check_permit_eligibility(
        user_profile.get("permit_type"),
        lot_row.get("allowed_permits", "all")
    )

    gender_ok = check_gender_eligibility(
        user_profile.get("gender"),
        lot_row.get("gender_access", "all")
    )

    residency_ok = check_residency_eligibility(
        user_profile.get("residency"),
        lot_row.get("allowed_residency", "all")
    )

    category_ok = check_category_eligibility(
        user_profile.get("permit_type"),
        lot_row.get("category", "all")
    )

    time_ok = check_time_eligibility(
        user_profile.get("arrival_time", "00:00"),
        lot_row.get("time_rules", "all")
    )

    restricted_ok = check_restricted_status(lot_row)

    return permit_ok and gender_ok and residency_ok and category_ok and time_ok and restricted_ok


def get_eligibility_details(user_profile, lot_row):
    """
    Return detailed eligibility results for explanation in the UI.
    """
    permit_ok = check_permit_eligibility(
        user_profile.get("permit_type"),
        lot_row.get("allowed_permits", "all")
    )

    gender_ok = check_gender_eligibility(
        user_profile.get("gender"),
        lot_row.get("gender_access", "all")
    )

    residency_ok = check_residency_eligibility(
        user_profile.get("residency"),
        lot_row.get("allowed_residency", "all")
    )

    category_ok = check_category_eligibility(
        user_profile.get("permit_type"),
        lot_row.get("category", "all")
    )

    time_ok = check_time_eligibility(
        user_profile.get("arrival_time", "00:00"),
        lot_row.get("time_rules", "all")
    )

    restricted_ok = check_restricted_status(lot_row)

    return {
        "permit_ok": permit_ok,
        "gender_ok": gender_ok,
        "residency_ok": residency_ok,
        "category_ok": category_ok,
        "time_ok": time_ok,
        "restricted_ok": restricted_ok,
        "eligible": permit_ok and gender_ok and residency_ok and category_ok and time_ok and restricted_ok
    }
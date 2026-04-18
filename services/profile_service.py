"""Profile completeness service."""


def compute_profile_completeness(cursor, bo_user_id: str) -> dict:
    """Calculate profile completeness percentage and write to DB."""
    cursor.execute("""
        SELECT BusinessName, BusinessLogoUrl, BusinessDescription, PhoneNumber,
               BusinessAddress, BusinessCategory, ProfilePhotoUrl,
               FacebookLink, InstagramLink, WebsiteLink
        FROM BusinessOwnerProfile WHERE UserId = ? AND IsDeleted = 0
    """, (bo_user_id,))
    row = cursor.fetchone()
    if not row:
        return {"error": "Profile not found"}

    fields = list(row)
    field_names = ["BusinessName", "Logo", "Description", "Phone", "Address", "Category", "Photo",
                   "Facebook", "Instagram", "Website"]
    filled = sum(1 for f in fields if f and str(f).strip())
    pct = round((filled / len(fields)) * 100)

    # Check onboarding progress
    cursor.execute("""
        SELECT TourCompleted, ChecklistProductAdded, ChecklistPaymentSet, ChecklistProfileDone
        FROM OnboardingProgress WHERE BusinessOwnerId = ?
    """, (bo_user_id,))
    onb_row = cursor.fetchone()
    if onb_row:
        checklist_done = sum(1 for v in onb_row if v)
        pct = min(100, pct + (checklist_done * 5))

    # Check if has products
    cursor.execute("""
        SELECT COUNT(*) FROM Products
        WHERE BusinessOwnerProfileId IN (SELECT Id FROM BusinessOwnerProfile WHERE UserId = ?)
        AND IsDeleted = 0
    """, (bo_user_id,))
    prod_count = (cursor.fetchone() or [0])[0]
    if prod_count > 0:
        pct = min(100, pct + 10)

    cursor.execute("""
        UPDATE BusinessOwnerProfile SET ProfileCompletenessPct = ? WHERE UserId = ?
    """, (pct, bo_user_id))

    return {"user_id": bo_user_id, "profile_completeness": pct}


def compute_all_profiles(cursor) -> list:
    """Compute profile completeness for all BOs."""
    cursor.execute("SELECT UserId FROM BusinessOwnerProfile WHERE IsDeleted=0")
    ids = [r[0] for r in cursor.fetchall()]
    results = []
    for uid in ids:
        try:
            results.append(compute_profile_completeness(cursor, uid))
        except Exception as e:
            results.append({"user_id": uid, "error": str(e)})
    return results

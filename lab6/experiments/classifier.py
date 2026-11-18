def classify_salary(amount: float) -> str:
    if amount >= 60_000:
        return "high"
    if amount >= 30_000:
        return "medium"
    return "low"
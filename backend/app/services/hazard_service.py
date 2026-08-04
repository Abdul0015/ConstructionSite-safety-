def categorize_hazard(description: str) -> str:
    """
    Rule-based keyword & metadata hazard categorization engine.
    Categorizes hazards into: electrical, structural, fire, tripping, chemical, or other.
    """
    if not description:
        return "other"

    desc_lower = description.lower()

    if any(k in desc_lower for k in ["wire", "cable", "shock", "spark", "electric", "power", "circuit"]):
        return "electrical"
    elif any(k in desc_lower for k in ["crack", "collapse", "scaffold", "beam", "wall", "foundation", "structural"]):
        return "structural"
    elif any(k in desc_lower for k in ["fire", "smoke", "flame", "combustible", "fuel", "burning"]):
        return "fire"
    elif any(k in desc_lower for k in ["trip", "fall", "slip", "spill", "debris", "hole", "wet"]):
        return "tripping"
    elif any(k in desc_lower for k in ["chemical", "acid", "toxic", "gas", "fume", "solvent"]):
        return "chemical"
    else:
        return "other"

"""Keyword configuration for the scoring engine (SPEC §7).

Each entry maps a canonical tag -> (weight, list of match phrases). Tune these
freely — they're the main lever on what the report surfaces. Phrases match
case-insensitively as whole words/phrases.
"""
from __future__ import annotations

# --- Design fit: what kind of work it is -------------------------------------
DESIGN_KEYWORDS: dict[str, tuple[float, list[str]]] = {
    "branding": (1.0, ["branding", "brand identity", "brand strategy"]),
    "rebrand": (1.0, ["rebrand", "rebranding", "brand refresh"]),
    "visual_identity": (1.0, ["visual identity", "logo", "identity system"]),
    "website_redesign": (1.0, ["website redesign", "web redesign", "website design", "web design", "redesign of the website"]),
    "ux_ui": (0.9, ["ux", "ui", "user experience", "user interface", "ux/ui"]),
    "design_system": (0.9, ["design system", "component library", "style guide"]),
    "communications_strategy": (0.8, ["communications strategy", "comms strategy", "communication strategy"]),
    "editorial_design": (0.8, ["editorial design", "publication design", "layout design"]),
    "campaign_assets": (0.7, ["campaign assets", "marketing collateral", "creative campaign", "advertising campaign"]),
    "annual_report": (0.7, ["annual report"]),
    "graphic_design": (0.6, ["graphic design", "graphic designer"]),
    "creative_services": (0.5, ["creative services", "design services", "creative agency"]),
}

# --- Sector fit: who the buyer is --------------------------------------------
SECTOR_KEYWORDS: dict[str, tuple[float, list[str]]] = {
    "nonprofit": (1.0, ["nonprofit", "non-profit", "ngo", "charitable", "charity"]),
    "foundation": (1.0, ["foundation", "philanthropy", "philanthropic", "grantmaking"]),
    "arts_culture": (1.0, ["arts", "culture", "cultural", "museum", "gallery", "theater", "theatre"]),
    "public_health": (0.9, ["public health", "health equity", "community health"]),
    "civic_government": (0.9, ["civic", "government transparency", "open government", "public sector"]),
    "education": (0.8, ["education", "university", "college", "school", "academic"]),
    "climate": (0.9, ["climate", "sustainability", "environmental", "conservation"]),
    "media_journalism": (0.8, ["media", "journalism", "newsroom", "public media", "broadcasting"]),
}

# --- Penalties: disqualifying / off-target work ------------------------------
PENALTY_KEYWORDS: dict[str, tuple[float, list[str]]] = {
    "construction": (25.0, ["construction", "building renovation", "general contractor"]),
    "infrastructure_engineering": (25.0, ["infrastructure engineering", "civil engineering", "roadway", "bridge", "water treatment"]),
    "it_systems": (20.0, ["erp", "saas implementation", "network infrastructure", "server procurement", "software license", "it support services"]),
    "staffing": (20.0, ["staffing services", "temporary staffing", "staff augmentation", "recruitment services"]),
    "hardware": (20.0, ["hardware procurement", "equipment purchase", "computer hardware", "office supplies"]),
}

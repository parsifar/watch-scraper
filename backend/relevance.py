import re
from typing import List, Set


# ============================================================
# Configuration
# ============================================================

# Keywords that strongly indicate accessories, not watches
ACCESSORY_KEYWORDS = {
    "strap", "band", "bracelet", "replacement", "rubber",
    "leather", "silicone", "nylon", "nato", "link", "links",
    "buckle", "clasp", "guard", "guards", "adapter", "adapters", "case"
}

# Generic words that should not heavily influence relevance
STOPWORDS = {
    "watch", "watches", "mens", "men", "women", "ladies",
    "automatic", "quartz", "digital", "analog",
    "black", "silver", "gold", "steel", "stainless"
}

# Define feature keywords
FEATURE_KEYWORDS = {
    "solar", "eco", "eco-drive", "kinetic",
    "automatic", "mechanical", "quartz",
    "titanium", "diver", "chronograph"
}


# ============================================================
# Normalization & Tokenization
# ============================================================

def normalize(text: str) -> str:
    """
    Normalize text for comparison:
    - lowercase
    - remove punctuation
    - normalize whitespace
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    """
    Split normalized text into tokens.
    """
    return text.split()


# ============================================================
# Model Token Extraction
# ============================================================

def is_model_token(token: str) -> bool:
    """
    Determine whether a token looks like a watch model code.

    Requires:
    - at least 2 letters
    - at least 2 digits

    This avoids false positives like:
    - 200m
    - wr100
    - iso6425
    """
    letters = sum(c.isalpha() for c in token)
    digits = sum(c.isdigit() for c in token)
    return letters >= 2 and digits >= 2


def extract_model_tokens(text: str) -> Set[str]:
    """
    Extract model-like tokens from text.

    Handles:
    - GA700
    - GA 700
    - SNXS77K1
    """
    tokens = tokenize(normalize(text))
    combined = []
    skip = False

    for i, t in enumerate(tokens):
        if skip:
            skip = False
            continue

        # Combine letter token + numeric token (e.g. "ga" + "700")
        if t.isalpha() and i + 1 < len(tokens) and tokens[i + 1].isdigit():
            combined.append(t + tokens[i + 1])
            skip = True
        else:
            combined.append(t)

    return {t for t in combined if is_model_token(t)}


# ============================================================
# Base Model Logic (CRITICAL FIX)
# ============================================================

def base_model(token: str) -> str:
    """
    Extract the base model for comparison.

    Logic:
    - Take starting letters
    - Take first numeric sequence
    - Ignore extra suffix letters/digits
    """
    letters = []
    digits = []
    found_digit = False

    for c in token:
        if c.isalpha() and not found_digit:
            letters.append(c)
        elif c.isdigit():
            digits.append(c)
            found_digit = True
        elif found_digit:
            # stop at first non-digit after numeric sequence
            break

    return "".join(letters + digits)


# ============================================================
# Series / Line Query Detection
# ============================================================

def is_series_query(query: str) -> bool:
    """
    Detect searches like:
    - "seiko 5"
    - "tissot prx"
    - "citizen eco drive"

    Characteristics:
    - no explicit model tokens
    - presence of digits or short series words
    """
    q_models = extract_model_tokens(query)
    q_tokens = tokenize(normalize(query))

    return (
        not q_models
        and any(token.isdigit() for token in q_tokens)
    )

# ============================================================
# Feature Query Detection
# ============================================================


def is_feature_query(query: str) -> bool:
    tokens = set(tokenize(normalize(query)))
    return bool(tokens & FEATURE_KEYWORDS)

# ============================================================
# Accessory Detection
# ============================================================


WATCH_KEYWORDS = {
    "analog", "digital", "quartz", "automatic", "chronograph"
}

ACCESSORY_TRIGGERS = {"for", "fits", "compatible with"}


def accessory_penalty(text: str) -> int:
    """
    Apply a negative penalty for accessory listings like straps or bands.

    Logic:
    1. If an accessory keyword is present:
        a. AND the text contains a trigger phrase like "for GA-2100" or "fits GA-2100"
        b. AND it does NOT contain watch-function keywords
       → High penalty (-15)

    2. If accessory keywords appear but watch keywords are also present
       → Likely a real watch, ignore accessory keywords (penalty 0)

    3. If accessory keywords appear in ambiguous context
       → Mild penalty (-5)
    """
    tokens = set(tokenize(normalize(text)))
    lower_text = normalize(text)

    has_accessory_kw = bool(tokens & ACCESSORY_KEYWORDS)
    has_watch_kw = bool(tokens & WATCH_KEYWORDS)

    # Quick keep: real watches
    if has_watch_kw:
        return 0

    # Detect trigger phrases with model presence
    for trigger in ACCESSORY_TRIGGERS:
        if trigger in lower_text:
            # Likely "strap for GA-2100" → real accessory
            return -15

    # If accessory keyword exists but no watch keywords and no trigger phrases
    if has_accessory_kw:
        # Ambiguous accessory (could be part of model description)
        return -5

    # Default: no penalty
    return 0


# ============================================================
# Relevance Scoring
# ============================================================

def relevance_score(query: str, product_name: str) -> float:
    """
    Compute relevance score between a search query
    and a scraped product title.
    """
    score = 0.0

    q_norm = normalize(query)
    p_norm = normalize(product_name)

    q_tokens = set(tokenize(q_norm)) - STOPWORDS
    p_tokens = set(tokenize(p_norm)) - STOPWORDS

    q_models = extract_model_tokens(q_norm)
    p_models = extract_model_tokens(p_norm)

    series_query = is_series_query(query)

    # --------------------------------------------------------
    # 1. Exact model token match (strongest signal)
    # --------------------------------------------------------
    exact_matches = q_models & p_models
    score += len(exact_matches) * 8

    # --------------------------------------------------------
    # 2. Base model (family) match (variant support)
    # --------------------------------------------------------
    for qm in q_models:
        for pm in p_models:
            if base_model(qm) == base_model(pm):
                score += 6

    # --------------------------------------------------------
    # 3. Wrong model family penalty (ONLY if model was specified)
    # --------------------------------------------------------
    if q_models and p_models and not series_query:
        if not any(
            base_model(qm) == base_model(pm)
            for qm in q_models
            for pm in p_models
        ):
            score -= 4

    # --------------------------------------------------------
    # 4. Token overlap (weak signal)
    # --------------------------------------------------------
    score += len(q_tokens & p_tokens) * 0.5

    # --------------------------------------------------------
    # 5. Series phrase boost (e.g. "seiko 5")
    # --------------------------------------------------------
    if series_query:
        if q_norm in p_norm:
            score += 4

    # --------------------------------------------------------
    # 6. Feature phrase boost (e.g. "seiko 5")
    # --------------------------------------------------------
    feature_tokens = q_tokens & FEATURE_KEYWORDS
    if feature_tokens:
        score += len(feature_tokens & p_tokens) * 3

    # --------------------------------------------------------
    # 7. Accessory penalty
    # --------------------------------------------------------
    score += accessory_penalty(product_name)

    return score


# ============================================================
# Dynamic Thresholding
# ============================================================

def recommended_threshold(query: str) -> float:
    """
    Choose a relevance threshold based on the user's search intent.

    Intent types:
    1) Exact / family model search   -> high threshold
       e.g. "ga700", "snxs77"

    2) Series / line search          -> medium threshold
       e.g. "seiko 5", "tissot prx"

    3) Feature-based search          -> low threshold
       e.g. "casio solar", "titanium diver"

    4) Generic brand search          -> low threshold
       e.g. "casio watches"
    """

    normalized = normalize(query)
    tokens = set(tokenize(normalized))
    models = extract_model_tokens(normalized)

    # Feature intent (solar, automatic, diver, etc.)
    feature_intent = bool(tokens & FEATURE_KEYWORDS)

    # Series / line intent (numeric but no explicit model)
    series_intent = is_series_query(query)

    if models:
        # User typed a specific model or model family
        return 4.0

    if series_intent:
        # Brand + line (e.g. "seiko 5")
        return 2.5

    if feature_intent:
        # Feature-based discovery search
        return 1.5

    # Generic brand/category search
    return 2.0


# ============================================================
# Result Filtering
# ============================================================

def filter_results(query, results):
    """
    Score, filter, and sort scraped results.
    """
    threshold = recommended_threshold(query)
    scored = []

    for r in results:
        s = relevance_score(query, r["name"])
        if s >= threshold:
            scored.append({**r, "score": round(s, 2)})

    return sorted(scored, key=lambda x: x["score"], reverse=True)

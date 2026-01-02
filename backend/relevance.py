import re


def normalize(text: str) -> str:
    """Lowercase, remove punctuation, normalize spaces"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize(text: str) -> list[str]:
    """Split into simple tokens"""
    return text.split()


def is_model_token(token: str) -> bool:
    """Detect “model-like” tokens (has letters and numbers)"""
    return any(c.isalpha() for c in token) and any(c.isdigit() for c in token)


def extract_model_tokens(text: str) -> set[str]:
    """
    Extract model tokens.
    Handles both 'GA2100' and 'GA 2100' style tokens.
    """
    tokens = tokenize(normalize(text))
    combined = []
    skip_next = False

    for i, t in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue

        # Combine letter token + next numeric token (e.g., "ga" + "2100" → "ga2100")
        if t.isalpha() and i + 1 < len(tokens) and tokens[i + 1].isdigit():
            combined.append(t + tokens[i + 1])
            skip_next = True
        else:
            combined.append(t)

    # Keep only tokens that look like models
    return {t for t in combined if is_model_token(t)}


def numeric_part(token: str) -> str:
    """Extract numeric part of token"""
    return ''.join(c for c in token if c.isdigit())


def relevance_score(query: str, product_name: str) -> float:
    """Compute relevance between query and product"""
    q_models = extract_model_tokens(query)
    p_models = extract_model_tokens(product_name)

    score = 0.0

    # 1. Strong numeric model match
    for qm in q_models:
        q_num = numeric_part(qm)
        for pm in p_models:
            if q_num and q_num == numeric_part(pm):
                score += 5

    # 2. Partial token overlap
    q_tokens = set(tokenize(normalize(query)))
    p_tokens = set(tokenize(normalize(product_name)))
    score += len(q_tokens & p_tokens)

    # 3. Penalize wrong model numbers
    if p_models and q_models and score == 0:
        score -= 5

    return score


def filter_results(query, results, threshold=3):
    scored = []
    for r in results:
        s = relevance_score(query, r["name"])
        if s >= threshold:
            scored.append({**r, "score": s})
    return sorted(scored, key=lambda x: x["score"], reverse=True)

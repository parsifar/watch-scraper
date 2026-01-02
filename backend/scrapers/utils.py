import re


def normalize_price(price_str: str) -> float:
    cleaned = re.sub(r"[^\d.,]", "", price_str)

    if "," in cleaned:
        if "." in cleaned:
            # Decide by which comes last
            if cleaned.rfind(".") > cleaned.rfind(","):
                # US/CA: 1,299.99
                cleaned = cleaned.replace(",", "")
            else:
                # EU: 1.299,99
                cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            # Only comma → thousands separator (1,035)
            cleaned = cleaned.replace(",", "")

    try:
        return float(cleaned)
    except ValueError:
        return 0.0

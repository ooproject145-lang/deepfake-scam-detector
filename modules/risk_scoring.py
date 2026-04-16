def classify_score(score: int) -> str:
    if score >= 50:
        return "Likely Scam"
    elif score >= 25:
        return "Suspicious"
    return "Genuine"


def get_result_style(label: str) -> str:
    if label == "Likely Scam":
        return "result-danger"
    elif label == "Suspicious":
        return "result-warn"
    return "result-good"
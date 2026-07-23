"""
SM-2 Spaced Repetition Algorithm implementation.
Based on the SuperMemo-2 algorithm by Piotr Wozniak.
"""

from datetime import date, timedelta


def sm2_algorithm(ease_factor: float, interval: int, repetitions: int, quality: int) -> dict:
    """
    Calculate new spaced repetition parameters based on user's recall quality.

    Args:
        ease_factor: current ease factor (default 2.5)
        interval: current interval in days
        repetitions: consecutive correct repetitions
        quality: user's recall quality (0-5)
            0: complete blackout
            1: incorrect, but upon seeing the answer it felt familiar
            2: incorrect, but upon seeing the answer it seemed easy to remember
            3: correct, but required serious effort
            4: correct, after some hesitation
            5: correct, perfect recall

    Returns:
        dict with new ease_factor, interval, repetitions, next_review_date
    """
    if not 0 <= quality <= 5:
        raise ValueError("Quality must be between 0 and 5")

    if quality >= 3:
        # Correct response
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval * ease_factor)

        new_repetitions = repetitions + 1
    else:
        # Incorrect response - reset
        new_interval = 1
        new_repetitions = 0

    # Update ease factor
    new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if new_ease_factor < 1.3:
        new_ease_factor = 1.3

    next_review = date.today() + timedelta(days=new_interval)

    return {
        "ease_factor": round(new_ease_factor, 4),
        "interval": new_interval,
        "repetitions": new_repetitions,
        "next_review": next_review,
    }


def get_quality_label(quality: int) -> str:
    """Return a human-readable label for a quality score."""
    labels = {
        0: "完全忘记",
        1: "有点印象",
        2: "记得但犹豫",
        3: "努力后想起",
        4: "稍有犹豫",
        5: "完美记忆",
    }
    return labels.get(quality, "未知")


def get_status_label(ease_factor: float, repetitions: int) -> str:
    """Determine mastery status based on spaced repetition parameters."""
    if repetitions >= 5 and ease_factor >= 2.5:
        return "mastered"
    elif repetitions >= 2:
        return "reviewing"
    else:
        return "learning"

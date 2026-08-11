CATEGORY_KEYWORDS = {
    "Academic": ["assignment", "essay", "exam", "study", "homework", "lecture", "paper", "thesis", "course"],
    "Work": ["meeting", "email", "report", "presentation", "deadline", "project", "colleague", "boss", "client"],
    "Health": ["doctor", "appointment", "exercise", "workout", "gym", "medicine", "health", "fitness", "therapy"],
    "Personal": ["buy", "call", "visit", "clean", "organize", "plan", "birthday", "anniversary", "groceries"],
}

DEFAULT_CATEGORY = "Personal"


def classify_category(title: str, description: str | None = None) -> str:
    text = f"{title} {description or ''}".lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category

    return DEFAULT_CATEGORY

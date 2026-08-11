import pytest

from app.services.category_classifier import classify_category


@pytest.mark.parametrize(
    "title,description,expected",
    [
        ("Finish essay on climate change", "", "Academic"),
        ("Prepare presentation for the client", "", "Work"),
        ("Doctor appointment", "annual checkup", "Health"),
        ("Buy groceries", "milk, eggs, bread", "Personal"),
        ("Something with no matching keywords", "", "Personal"),
    ],
)
def test_classify_category(title, description, expected):
    assert classify_category(title, description) == expected


def test_classification_is_case_insensitive():
    assert classify_category("STUDY for EXAM", "") == "Academic"

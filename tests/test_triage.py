import pytest

from src.schemas import TicketCategory, TicketTriageResult, PriorityLevel
from src.service import TicketTriageService
from tests.test_data import EVAL_DATASET


@pytest.fixture(scope="function")
def triage_service() -> TicketTriageService:
    """Create a fresh service instance per test to avoid event-loop reuse issues."""
    return TicketTriageService()


@pytest.mark.asyncio
async def test_structure_validation(triage_service: TicketTriageService):
    """Check if the response meets the schema contract."""
    ticket = "I need to install Docker on my dev laptop"

    result = await triage_service.analyze_ticket(ticket)

    assert isinstance(result, TicketTriageResult)
    assert isinstance(result.category, TicketCategory)
    assert isinstance(result.priority, PriorityLevel)
    assert 0.0 <= result.confidence_score <= 1.0
    assert len(result.summary) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize("case", EVAL_DATASET, ids=[c["id"] for c in EVAL_DATASET])
async def test_behavioral_evals(triage_service: TicketTriageService, case: dict):
    """Quality evaluation on EVAL_DATASET."""
    result = await triage_service.analyze_ticket(case["ticket_text"])

    expected_category = str(case["expected_category"]).lower()
    assert result.category.value.lower() == expected_category, (
        f"Invalid category for case {case['id']}. "
        f"Expected {expected_category}, got {result.category.value}"
    )


    priority_map = {
        "low": 0,
        "medium": 1,
        "high": 2,
        "critical": 3
    }

    expected_min_priority = priority_map[str(case["expected_min_priority"]).lower()]
    result_priority = priority_map[str(result.priority.value.lower())]

    assert result_priority >= expected_min_priority, (
        f"Invalid priority for case {case['id']}. "
        f"Expected {expected_min_priority}, got {result.priority.value}"
    )

    

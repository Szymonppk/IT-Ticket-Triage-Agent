from enum import Enum
from pydantic import BaseModel, Field, ValidationError

class TicketCategory(str, Enum):
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    NETWORK = "Network"
    ACCESS = "Access & Security"
    OTHER = "Other"

class PriorityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class TicketTriageResult(BaseModel):
    category: TicketCategory = Field(description="Main Category of the IT ticket")
    priority: PriorityLevel = Field(description="Priority Level of the IT ticket")
    summary: str = Field(description="Description of the IT ticket")
    confidence_score: float = Field(description="Confidence score of the triage result", ge=0.0, le=1.0)

def main():
    print("Checking valid payload...")
    valid_payload = {
        "category": "Software",
        "priority": "High",
        "summary":"App crashes on launch",
        "confidence_score": 0.95
    }

    try:
        result_valid = TicketTriageResult(**valid_payload)
        print("Triage Result: ", result_valid.model_dump_json(indent=2))
    except ValidationError as e:
        print("Validation error: ", e)

    print("Checking invalid payload...")

    valid_payload["category"] = "InvalidCategory" 

    try:
        result_unvalid = TicketTriageResult(**valid_payload)

        print("Triage Result:", result_unvalid.model_dump_json(indent=2))
    except ValidationError as e:
        print("Validation error: ", e)


if __name__ == "__main__":
    main()








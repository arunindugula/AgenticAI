import json
from pydantic import BaseModel, Field


class ReportingServiceArgs(BaseModel):
    summary: str = Field(description="Summary of the issue to be escalated")

class ReportingService:
    def __init__(self):
        pass

    @staticmethod
    def escalate_to_engineer(summary: str) -> str:
        """
        ### TODO: Implement this function.
        1. Print a message saying "-> TOOL: Escalating to human..."
        2. Return a JSON string confirming the ticket was created.
        """
        print(f"-> TOOL: Escalating to human with summary: {summary}...")
        return json.dumps({"status": "success", 
                           "message": "Ticket created, Escalated to human"})

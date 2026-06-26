import json
from pydantic import BaseModel, Field

class ServiceHandlerArgs(BaseModel):
    server_id: str = Field(description="The ID of the server to restart")

class ServiceHandler:
    def __init__(self):
        pass

    @staticmethod
    def restart_service(server_id: str) -> str:
        """
        ### TODO: Implement this function.
        1. Print a message saying "-> TOOL: Restarting service..."
        2. Return a JSON string confirming the restart was successful.
        Example return: '{"status": "success", "message": "Server restarted successfully"}'
        """
        print(f"-> TOOL: Restarting service {server_id}...")
        return json.dumps({"status": "success","server_id": server_id, "message": "Server restarted successfully"})


import json
from pydantic import BaseModel, Field


class ServerHealthArgs(BaseModel):
    server_id: str = Field(description="The ID of the server to check health for")

class ServerHealth:
    def __init__(self):
        pass

    @staticmethod
    def get_server_health(server_id: str) -> str:
        """Returns CPU and Memory usage for a given server. Mock data"""
        print(f"-> TOOL: Checking health for {server_id}...")

        metrics = {
            # Scenario 1: High CPU (Needs Restart)
            "payment-server-01": {"cpu": "98%", "memory": "40%", "status": "Warning"},

            # Scenario 2: Healthy (No Action Needed)
            "db-node-02": {"cpu": "12%", "memory": "60%", "status": "Healthy"},

            # Scenario 3: High Memory Leak (Needs Restart or Escalation)
            "auth-service-03": {"cpu": "45%", "memory": "95%", "status": "Critical"},

            # Scenario 4: Network/Dependency Failure (Needs Escalation)
            "search-index-09": {"cpu": "10%", "memory": "15%", "status": "Error"},

            # Scenario 5: Completely Normal
            "frontend-node-04": {"cpu": "25%", "memory": "30%", "status": "Healthy"},
        }

        result = metrics.get(server_id, {"error": "Server not found. Check the ID."})
        return json.dumps(result)

            

    
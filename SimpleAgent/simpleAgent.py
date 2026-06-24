import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
import json

from logHandler import LogHandler, LogHandlerArgs
from reportingSrvice import ReportingService, ReportingServiceArgs
from serverHealth import ServerHealth, ServerHealthArgs
from serviceHandler import ServiceHandler, ServiceHandlerArgs


class SimpleAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_APIKEY"))
        self. AVAILABLE_FUNCTIONS = {
            "fetch_recent_logs": LogHandler.fetch_recent_logs,
            "escalate_to_engineer": ReportingService.escalate_to_engineer,
            "get_server_health": ServerHealth.get_server_health,
            "restart_service": ServiceHandler.restart_service
        }

        self.myTools = [openai.pydantic_function_tool(model=LogHandlerArgs, name="fetch_recent_logs", description="Retrieves the most recent log entries from a server to diagnose errors."), 
           openai.pydantic_function_tool(model=ReportingServiceArgs, name="escalate_to_engineer", description="Escalates an issue to a human engineer."), 
           openai.pydantic_function_tool(model=ServerHealthArgs, name="get_server_health", description="Retrieves the CPU and Memory usage for a specific server."), 
           openai.pydantic_function_tool(model=ServiceHandlerArgs, name="restart_service", description="Restarts a service on a specific server.")]

    def run_it_agent(self,user_issue: str):
        print(f"\n--- New Incident: {user_issue} ---")
        messages = [
            {"role": "system", "content": "You are a Level 1 IT Responder. Investigate server issues. "
                                            "If CPU or Memory is > 90%, restart the service. If logs show critical dependency errors (like connection refused) that a restart won't fix, escalate to an engineer."},
            {"role": "user", "content": user_issue}
        ]

        collected_data = {}

        while True:
            print("\n[AI Thinking...]")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.myTools,
                tool_choice="auto"
            )

            response_msg = response.choices[0].message
            messages.append(response_msg)

            print(response)

            if response_msg.tool_calls:
                for tool_call in response_msg.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    # Retrieve the actual python function based on name
                    function_to_call = self.AVAILABLE_FUNCTIONS.get(func_name)

                    if function_to_call:
                        # Execute the function
                        tool_output = function_to_call(**func_args)
                        collected_data [func_name] = json.loads(tool_output)
                    
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id, 
                            "name": func_name,        
                            "content": tool_output      
                        })

            else:
                print(f"\n[FINAL RESPONSE]: {response_msg.content}")
                print("\n" + "="*80 + "\n")
                break

if __name__ == "__main__":
    load_dotenv()

    Agent = SimpleAgent()

    while True:
        choices = "\t 1: Should trigger a restart (CPU is 98%)\n"
        choices += "\t 2: Something is wrong with db-node-02\n"
        choices += "\t 3: The High Memory Case (auth-service-03)\n"
        choices += "\t 4: The Dependency Failure (search-index-09)\n"
        choices += "\t 5: The Healthy Server (frontend-node-04)\n"
        choices += "\t 6: Exit\n"
        choices += "Enter Choice: "
        user_input = input(choices)
        if user_input == "1":
            # Scenario A: Should trigger a restart (CPU is 98%)
            Agent.run_it_agent("The payment-server-01 is extremely slow and timing out.")
        elif user_input == "2":
            # Scenario B: Should trigger an escalation (DB is healthy but logs might be weird)
            Agent.run_it_agent("Something is wrong with db-node-02")
        elif user_input == "3":
            # Scenario C: The High Memory Case (auth-service-03)
            # Agent should see Memory 95% + OutOfMemoryError logs -> Restart
            Agent.run_it_agent("Users are reporting login failures on auth-service-03.")
        elif user_input == "4":
            # Scenario D: The Dependency Failure (search-index-09)
            # Agent should see healthy CPU but "Connection Refused" logs -> Escalate
            Agent.run_it_agent("Search isn't working. Can you check search-index-09?")
        elif user_input == "5":
            # Scenario E: The Healthy Server (frontend-node-04)
            # Agent should see normal stats and 200 OK logs -> Do nothing / Report healthy
            Agent.run_it_agent("Check frontend-node-04 just to be safe.")
        else:
            break

The Autonomous IT Support Agent

This is a sample prototype for the Level 1 IT Incident Responder.


Objective: An AI agent that acts as the "first responder" for server incidents. It must:

Investigate: Check server health and logs when a user reports an issue.
Act: If CPU is critical (>90%), it should Restart the service.
Escalate: If the issue is complex or logs show a major problem it should Escalate to a human.

To run: 
1. create a .env file, example provided in env.example. Provide your own key.
2. pip install -r requirements.txt
3. python simpleAgent.py
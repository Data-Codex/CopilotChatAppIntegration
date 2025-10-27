
https://community.fabric.microsoft.com/t5/Fabric-platform/Does-Fabric-Data-agent-support-Managed-Identity-or-Service/m-p/4685958#M15611



from azure.identity import ManagedIdentityCredential
from fabric_data_agent_client import FabricDataAgentClient
import json

# ────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────
TENANT_ID = ""
DATA_AGENT_URL = "<your_fabric_data_agent_url>" 
QUESTION = "Question"

# ────────────────────────────────────────────────
# Authentication using Managed Identity
# ────────────────────────────────────────────────
print("Authenticating with Managed Identity...")
credential = ManagedIdentityCredential()

# Request Fabric API token
token = credential.get_token("https://api.fabric.microsoft.com/.default").token
print("Authentication successful using Managed Identity.")

# ────────────────────────────────────────────────
# Initialize Fabric Data Agent client
# ────────────────────────────────────────────────
client = FabricDataAgentClient(TENANT_ID, DATA_AGENT_URL)

# ────────────────────────────────────────────────
# Send question to Fabric Data Agent
# ────────────────────────────────────────────────
print(f"Sending question to Fabric Data Agent: {QUESTION}")
response = client.ask(QUESTION, token)
print("Response received from Fabric Data Agent.")

# ────────────────────────────────────────────────
# Retrieve run details
# ────────────────────────────────────────────────
try:
    run_details = client.get_run_details(QUESTION)
    messages = run_details.get('messages', {}).get('data', [])
    assistant_messages = [msg for msg in messages if msg.get('role') == 'assistant']

    if assistant_messages:
        final = assistant_messages[-1]['content']
        if isinstance(final, list) and final[0].get('type') == 'text':
            print("\nAssistant Response:")
            print(final[0]['text']['value'])
        else:
            print("\nFinal Answer Object:")
            print(json.dumps(final, indent=2))
    else:
        print("No assistant response found.")
except Exception as e:
    print(f"Error getting run details: {e}")



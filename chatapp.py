from azure.identity import InteractiveBrowserCredential
from fabric_data_agent_client import FabricDataAgentClient
 
TENANT_ID = ""
DATA_AGENT_URL = ""
 
print("Authenticating with Azure...")
credential = InteractiveBrowserCredential(tenant_id=TENANT_ID)
token = credential.get_token("https://api.fabric.microsoft.com/.default").token
print("Authentication successful.")
 
client = FabricDataAgentClient(TENANT_ID, DATA_AGENT_URL)
 
question = "Question"
print("Sending question to Fabric Data Agent...")
response = client.ask(question, token)
print("Response received.")
 
try:
    run_details = client.get_run_details(question)
    messages = run_details.get('messages', {}).get('data', [])
    assistant_messages = [msg for msg in messages if msg.get('role') == 'assistant']
 
    if assistant_messages:
        final = assistant_messages[-1]['content']
        if isinstance(final, list) and final[0].get('type') == 'text':
            print("\n" + final[0]['text']['value'])
        else:
            print("\nFinal Answer:")
            print(final)
    else:
        print("No assistant response found.")
except Exception as e:
    print(f"❌ Error getting run details: {e}")
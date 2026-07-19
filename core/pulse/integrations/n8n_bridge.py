"""
n8n Webhook Bridge for NIA workflows.
Enables NIA to post states to local n8n instances for complex automation.
"""
import requests
import json

class N8NBridge:
    def __init__(self, webhook_url: str = "http://localhost:5678/webhook/nia"):
        self.webhook_url = webhook_url
        print(f"[Integrations] n8n Bridge pointing to {self.webhook_url}")

    def trigger_workflow(self, event_type: str, payload: dict) -> bool:
        """Posts a payload to an n8n webhook."""
        data = {
            "source": "NIA_Sovereign_OS",
            "event": event_type,
            "payload": payload
        }
        print(f"[Integrations] Triggering n8n workflow: {event_type}")
        try:
            # Uncomment for actual execution when n8n is running locally
            # response = requests.post(
            #     self.webhook_url, 
            #     json=data,
            #     headers={'Content-Type': 'application/json'},
            #     timeout=3
            # )
            # return response.status_code == 200
            
            # Mock success
            print(f"[Integrations] n8n payload dispatched: {json.dumps(data)}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[Integrations] n8n Bridge Error: {e}")
            return False

if __name__ == "__main__":
    bridge = N8NBridge()
    bridge.trigger_workflow("share_screenshot", {"file": "desktop_1", "destination": "whatsapp"})

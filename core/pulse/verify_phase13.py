import asyncio
import logging
from agents.device_controller import DeviceController
from unified_controller import UnifiedController

logging.basicConfig(level=logging.INFO)

async def test_sovereignty():
    print("\n--- NIA SOVEREIGNTY VERIFICATION ---")
    
    controller = UnifiedController()
    
    print("\n1. Testing 'Click' with Verification and Pulse Sync...")
    # This should trigger _notify_pulse(True), then click, then verify, then _notify_pulse(False)
    # We use a logical command that triggers a mock click in current UnifiedController
    await controller.execute_complex_goal("Please click the middle of the screen")
    
    print("\n2. Testing Autonomous Session with Verification...")
    await controller.start_autonomous_session("Automate these 3 clicks")

    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_sovereignty())

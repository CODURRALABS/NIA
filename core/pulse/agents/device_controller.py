"""
DeviceController: Handles autonomous screen/input control for NIA.
Integrates VisionModule for spatial grounding and PyAutoGUI for execution.
"""
import pyautogui
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
from vision.vision_module import VisionModule
from vision.world_model import WorldModel
import logging

logger = logging.getLogger("DeviceController")

class DeviceController:
    def __init__(self):
        self.vision = VisionModule()
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.world_model = WorldModel()
        # Safety: move mouse to corner to abort
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5 # Add a small pause between pyautogui commands

    def execute_action(self, action_type: str, params: dict, verify: bool = True):
        """
        Executes a specific UI action with optional verification.
        action_type: 'click', 'type', 'scroll', 'press', 'drag'
        params: {'x': float, 'y': float, 'text': str, 'key': str, etc.}
        """
        before_img = None
        prediction = None
        if verify:
            before_img = self.vision.capture_viewport()
            # Subconscious Simulation (Phase 18)
            prediction = self.world_model.predict_action_outcome(action_type, params, "Sovereign desktop environment")

        try:
            if action_type == "click":
                x, y = self.vision.map_coordinate(params.get('x', 0.5), params.get('y', 0.5))
                logger.info(f"Clicking at ({x}, {y})")
                
                # Use pynput for better accuracy/compatibility
                self.mouse.position = (x, y)
                time.sleep(0.1)
                self.mouse.click(Button.left, 1)
            
            elif action_type == "type":
                text = params.get('text', '')
                logger.info(f"Typing: '{text}'")
                self.keyboard.type(text)
                
            elif action_type == "scroll":
                amount = params.get('amount', -100)
                logger.info(f"Scrolling: {amount}")
                pyautogui.scroll(amount)
                
            elif action_type == "press":
                key_name = params.get('key', 'enter')
                logger.info(f"Pressing key: {key_name}")
                # Map simple string keys to pynput keys if needed
                if hasattr(Key, key_name):
                    self.keyboard.press(getattr(Key, key_name))
                    self.keyboard.release(getattr(Key, key_name))
                else:
                    self.keyboard.press(key_name)
                    self.keyboard.release(key_name)

            elif action_type == "right_click":
                x, y = self.vision.map_coordinate(params.get('x', 0.5), params.get('y', 0.5))
                logger.info(f"Right-clicking at ({x}, {y})")
                self.mouse.position = (x, y)
                time.sleep(0.1)
                self.mouse.click(Button.right, 1)

            elif action_type == "double_click":
                x, y = self.vision.map_coordinate(params.get('x', 0.5), params.get('y', 0.5))
                logger.info(f"Double-clicking at ({x}, {y})")
                self.mouse.position = (x, y)
                time.sleep(0.1)
                self.mouse.click(Button.left, 2)

            elif action_type == "drag_to":
                x1, y1 = self.vision.map_coordinate(params.get('x1', 0.5), params.get('y1', 0.5))
                x2, y2 = self.vision.map_coordinate(params.get('x2', 0.5), params.get('y2', 0.5))
                logger.info(f"Dragging from ({x1}, {y1}) to ({x2}, {y2})")
                pyautogui.moveTo(x1, y1)
                pyautogui.dragTo(x2, y2, duration=1.0)

            if verify and before_img:
                time.sleep(1.0) # Wait for animation to finish
                after_img = self.vision.capture_viewport()
                diff_score = self.vision.get_pixel_diff(before_img, after_img)
                logger.info(f"Action '{action_type}' verification diff score: {diff_score:.2f}%")
                
                # Use WorldModel to validate the state change
                is_valid = self.world_model.validate_actual_state(diff_score, {"status": "changed"})
                
                if not is_valid:
                    logger.warning(f"Action '{action_type}' verification FAILED world model criteria.")
                    return False
                return True

        except Exception as e:
            logger.error(f"Failed to execute {action_type}: {e}")
            return False

        return True

    def watch_and_control(self, goal: str):
        """
        Recursive loop: Speak -> See -> Act.
        """
        print(f"[Device] Starting autonomous control loop for goal: {goal}")
        # 1. Capture Screen
        screenshot = self.vision.capture_viewport()
        
        # 2. Logic (Mocking LLM reasoning for coords)
        print(f"[Device] Analyzing screen for goal: {goal}")
        time.sleep(1)
        
        # 3. Act (Example: Click center)
        self.execute_action("click", {"x": 0.5, "y": 0.5})
        print("[Device] Action complete.")

if __name__ == "__main__":
    controller = DeviceController()
    controller.execute_action("click", {"x": 0.5, "y": 0.5})

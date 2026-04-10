#!/usr/bin/env python3
"""
SolidWorks Assembly Automation System
Step 1: Python foundation with screen control and AI integration
"""

import pyautogui
import time
import json
import base64
from PIL import Image
import io
import subprocess
import os
from typing import Tuple, List, Dict, Any

class SolidWorksAutomation:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        self.screen_width, self.screen_height = pyautogui.size()
        
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse coordinates"""
        return pyautogui.position()
    
    def click_at(self, x: int, y: int, clicks: int = 1, interval: float = 0.1):
        """Click at specific coordinates"""
        pyautogui.click(x, y, clicks=clicks, interval=interval)
        
    def move_to(self, x: int, y: int, duration: float = 0.5):
        """Move mouse to coordinates"""
        pyautogui.moveTo(x, y, duration=duration)
        
    def take_screenshot(self, region: Tuple[int, int, int, int] = None, filename: str = None) -> str:
        """Take screenshot and save to system_images folder, return file path"""
        # Create system_images directory if it doesn't exist
        images_dir = os.path.join(os.getcwd(), "system_images")
        os.makedirs(images_dir, exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # Ensure proper path handling for spaces and special characters
        filepath = os.path.join(images_dir, filename)
        filepath = os.path.normpath(filepath)
        
        # Take screenshot
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(filepath)
        
        # Also return base64 for backward compatibility
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        buffer.seek(0)
        base64_data = base64.b64encode(buffer.getvalue()).decode()
        
        return filepath
    
    def find_image_on_screen(self, template_path: str, confidence: float = 0.8) -> List[Tuple[int, int]]:
        """Find template image on screen and return coordinates"""
        try:
    def launch_solidworks(self):
        """Launch SolidWorks application with flexible path detection"""
        possible_paths = [
            "C:\\Program Files\\SOLIDWORKS Corp\\SOLIDWORKS\\SLDWORKS.exe",
            "C:\\Program Files\\SOLIDWORKS 2024\\SOLIDWORKS\\SLDWORKS.exe",
            "C:\\Program Files\\SOLIDWORKS 2023\\SOLIDWORKS\\SLDWORKS.exe",
            "C:\\Program Files\\SOLIDWORKS 2022\\SOLIDWORKS\\SLDWORKS.exe",
            "C:\\Program Files\\SOLIDWORKS 2021\\SOLIDWORKS\\SLDWORKS.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    print(f"Launching SolidWorks from: {path}")
                    subprocess.Popen([path])
                    time.sleep(15)  # Wait longer for SolidWorks to fully load
                    return True
                except Exception as e:
                    print(f"Failed to launch from {path}: {e}")
                    continue
        
        print("Could not find SolidWorks installation. Please:")
        print("1. Ensure SolidWorks is installed")
        print("2. Or manually start SolidWorks before running this script")
        return False
            "C:\\Program Files\\SOLIDWORKS 2022\\SOLIDWORKS\\SLDWORKS.exe",
            "C:\\Program Files\\SOLIDWORKS 2021\\SOLIDWORKS\\SLDWORKS.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    print(f"Launching SolidWorks from: {path}")
                    subprocess.Popen([path])
                    time.sleep(15)  # Wait longer for SolidWorks to fully load
                    return True
                except Exception as e:
                    print(f"Failed to launch from {path}: {e}")
                    continue
        
        # Try to find via registry or system PATH
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\SolidWorks\\Applications\\SOLIDWORKS")
            install_path, _ = winreg.QueryValueEx(key, "InstallPath")
            exe_path = os.path.join(install_path, "SLDWORKS.exe")
            if os.path.exists(exe_path):
                subprocess.Popen([exe_path])
                time.sleep(15)
                return True
        except:
            pass
            
        print("Could not find SolidWorks installation. Please:")
        print("1. Ensure SolidWorks is installed")
        print("2. Or manually start SolidWorks before running this script")
        return False
    
    def create_assembly_project(self):
        """Create new assembly project"""
        # Wait for SolidWorks to be ready
        time.sleep(3)
        
        # Press Ctrl+N for new file
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(2)
        
        # Navigate to Assembly template (assuming standard SolidWorks layout)
        pyautogui.press('tab', presses=3, interval=0.3)
        pyautogui.press('enter')
        time.sleep(2)
        
    def wait_for_user_components(self) -> bool:
        """Wait for user to manually import all components"""
        print("Please import all components into the assembly manually...")
        print("Press Enter when ready to continue with automated assembly...")
        input()
        return True
    
    def analyze_screen_with_ai(self, image_base64: str) -> Dict[str, Any]:
        """Send screenshot to AI for analysis and get click coordinates"""
        # This is a placeholder for AI integration
        # In real implementation, this would call your AI vision model
        
        # Mock response for demonstration
        return {
            "components_found": [
                {"name": "bearing_housing", "x": 500, "y": 300, "action": "click"},
                {"name": "shaft", "x": 700, "y": 400, "action": "click"},
                {"name": "mate_button", "x": 800, "y": 600, "action": "click"}
            ],
            "confidence": 0.85,
            "next_step": "select_mate_type"
        }
    
    def perform_assembly_step(self, ai_instruction: Dict[str, Any]):
        """Perform single assembly step based on AI instruction"""
        for component in ai_instruction.get("components_found", []):
            x, y = component["x"], component["y"]
            action = component["action"]
            
            if action == "click":
                self.click_at(x, y)
                time.sleep(1)
            elif action == "double_click":
                self.click_at(x, y, clicks=2)
                time.sleep(1)
                
    def run_automation(self):
        """Main automation workflow"""
        print("Starting SolidWorks Assembly Automation...")
        
        # Step 1: Launch SolidWorks
        if not self.launch_solidworks():
            return False
            
        # Step 2: Create assembly project
        self.create_assembly_project()
        
        # Step 3: Wait for user to import components
        self.wait_for_user_components()
        
        # Step 4: Start automated assembly process
        print("Starting automated assembly process...")
        
        while True:
            # Take screenshot
            screenshot = self.take_screenshot()
            
            # Analyze with AI
            ai_response = self.analyze_screen_with_ai(screenshot)
            
            # Perform assembly step
            self.perform_assembly_step(ai_response)
            
            # Check if assembly complete
            if ai_response.get("next_step") == "assembly_complete":
                print("Assembly completed successfully!")
                break
                
            time.sleep(2)
        
        return True

if __name__ == "__main__":
    automation = SolidWorksAutomation()
    automation.run_automation()
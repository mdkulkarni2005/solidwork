#!/usr/bin/env python3
"""
Desktop-to-SolidWorks Assembly Automation Workflow
Follows exact steps: desktop -> SolidWorks -> assembly -> user import -> storage -> completion
"""

import base64
import json
import time
import os
import sqlite3
import subprocess
import platform
from typing import Dict, Any, List, Tuple
import pyautogui
import requests
from PIL import Image
import io

class DesktopAutomationWorkflow:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.nvidia_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.screen_width, self.screen_height = pyautogui.size()
        self.db_path = "assembly_workflow.db"
        self.setup_database()
        self.minimize_all_windows()
        
    def setup_database(self):
        """Initialize SQLite database for storing workflow data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                step_name TEXT NOT NULL,
                screenshot_base64 TEXT,
                ai_response TEXT,
                click_coordinates TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_name TEXT,
                file_path TEXT,
                import_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                assembly_step INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def minimize_all_windows(self):
        """Minimize all windows to show desktop"""
        if platform.system() == "Windows":
            # Windows: Win+D to show desktop
            pyautogui.hotkey('win', 'd')
            time.sleep(2)
        elif platform.system() == "Darwin":
            # macOS: Cmd+Alt+H to hide others
            pyautogui.hotkey('cmd', 'option', 'h')
            time.sleep(2)
        else:
            # Linux: Ctrl+Alt+D
            pyautogui.hotkey('ctrl', 'alt', 'd')
            time.sleep(2)
            
    def take_screenshot(self) -> str:
        """Take screenshot and return base64"""
        screenshot = pyautogui.screenshot()
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
        
    def store_workflow_step(self, step_name: str, screenshot: str, ai_response: str, coordinates: str):
        """Store workflow step in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO workflow_steps (step_name, screenshot_base64, ai_response, click_coordinates)
            VALUES (?, ?, ?, ?)
        ''', (step_name, screenshot, ai_response, coordinates))
        
        conn.commit()
        conn.close()
        
    def call_nvidia_ai(self, image_base64: str, objective: str) -> Dict[str, Any]:
        """Send screenshot to NVIDIA AI for analysis"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        Analyze this desktop screenshot and provide exact coordinates for: {objective}
        
        Return JSON format:
        {{
            "click_coordinates": [x, y],
            "confidence": 0.0-1.0,
            "element_description": "what you found",
            "next_action": "click|double_click|wait|complete",
            "reasoning": "brief explanation"
        }}
        
        Screen: {self.screen_width}x{self.screen_height}
        """
        
        payload = {
            "model": "mistralai/mistral-small-4-119b-2603",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_base64}"}
                        }
                    ]
                }
            ],
            "max_tokens": 300,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(self.nvidia_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            content = response.json()["choices"][0]["message"]["content"]
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "No JSON found", "click_coordinates": [0, 0], "confidence": 0}
                
        except Exception as e:
            return {"error": str(e), "click_coordinates": [0, 0], "confidence": 0}
            
    def click_at_coordinates(self, coordinates: List[int], action: str = "click"):
        """Execute click at given coordinates"""
        x, y = coordinates
        
        if action == "click":
            pyautogui.click(x, y)
        elif action == "double_click":
            pyautogui.doubleClick(x, y)
        elif action == "right_click":
            pyautogui.rightClick(x, y)
            
        print(f"Executed {action} at ({x}, {y})")
        
    def wait_for_solidworks_to_open(self, timeout: int = 30) -> bool:
        """Wait for SolidWorks to fully open"""
        print("Waiting for SolidWorks to open...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            screenshot = self.take_screenshot()
            analysis = self.call_nvidia_ai(screenshot, "Check if SolidWorks is now open and ready")
            
            if "solidworks" in str(analysis).lower() and analysis.get("confidence", 0) > 0.7:
                print("SolidWorks detected as open")
                return True
                
            time.sleep(2)
            
        print("Timeout waiting for SolidWorks to open")
        return False
        
    def find_assembly_button(self) -> Dict[str, Any]:
        """Find assembly button in SolidWorks"""
        screenshot = self.take_screenshot()
        return self.call_nvidia_ai(
            screenshot,
            "Find the 'Assembly' button/tab in SolidWorks interface (not Parts, not Drawing)"
        )
        
    def wait_for_user_imports(self) -> List[str]:
        """Wait for user to manually import components"""
        print("Please manually import all components into the assembly")
        print("Press Enter when all components are imported...")
        input()
        
        # Store user import information
        components = []
        print("Enter component names (one per line, empty to finish):")
        while True:
            component = input("Component name: ").strip()
            if not component:
                break
            components.append(component)
            
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for component in components:
            cursor.execute('''
                INSERT INTO user_imports (component_name)
                VALUES (?)
            ''', (component,))
            
        conn.commit()
        conn.close()
        
        return components
        
    def run_complete_workflow(self):
        """Execute complete desktop-to-assembly workflow"""
        print("=== Desktop-to-SolidWorks Assembly Automation ===")
        print("Starting from desktop...")
        
        # Step 1: Start from desktop (already minimized)
        print("Step 1: Desktop visible and ready")
        
        # Step 2: Find and click SolidWorks
        print("Step 2: Finding SolidWorks on desktop...")
        screenshot = self.take_screenshot()
        solidworks_analysis = self.call_nvidia_ai(
            screenshot,
            "Find SolidWorks application icon or shortcut on desktop and provide exact click coordinates"
        )
        
        if solidworks_analysis.get("confidence", 0) > 0.5:
            self.store_workflow_step(
                "find_solidworks",
                screenshot,
                json.dumps(solidworks_analysis),
                str(solidworks_analysis.get("click_coordinates", [0, 0]))
            )
            
            self.click_at_coordinates(solidworks_analysis["click_coordinates"])
            
            # Step 3: Wait for SolidWorks to open
            if self.wait_for_solidworks_to_open():
                
                # Step 4: Find assembly button
                print("Step 4: Finding assembly button...")
                assembly_analysis = self.find_assembly_button()
                
                if assembly_analysis.get("confidence", 0) > 0.5:
                    screenshot = self.take_screenshot()
                    self.store_workflow_step(
                        "find_assembly_button",
                        screenshot,
                        json.dumps(assembly_analysis),
                        str(assembly_analysis.get("click_coordinates", [0, 0]))
                    )
                    
                    self.click_at_coordinates(assembly_analysis["click_coordinates"])
                    
                    # Step 5: Wait for user imports
                    print("Step 5: Waiting for user to import components...")
                    user_components = self.wait_for_user_imports()
                    
                    print(f"User imported {len(user_components)} components: {user_components}")
                    
                    # Step 6: Continue automation with imported components
                    print("Step 6: Starting automated assembly with imported components...")
                    
                    # Here you would continue with the assembly automation
                    # using the imported components
                    
                    print("Workflow complete!")
                    return True
                    
        print("Workflow failed - check AI responses and try again")
        return False

if __name__ == "__main__":
    # Replace with your actual NVIDIA API key
    API_KEY = "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"
    
    automation = DesktopAutomationWorkflow(API_KEY)
    automation.run_complete_workflow()
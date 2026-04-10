#!/usr/bin/env python3
"""
NVIDIA AI-Powered Desktop Automation Agent
Takes screenshots, sends to NVIDIA AI, gets click coordinates, executes clicks
"""

import base64
import json
import time
import requests
from PIL import Image
import io
import pyautogui
import cv2
import numpy as np
from typing import Dict, List, Tuple, Any

class NVIDIAAutomationAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.screen_width, self.screen_height = pyautogui.size()
        pyautogui.FAILSAFE = True
        
    def take_screenshot(self) -> str:
        """Take screenshot and return base64 encoded image"""
        screenshot = pyautogui.screenshot()
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
    
    def analyze_screen_with_nvidia(self, image_base64: str, objective: str) -> Dict[str, Any]:
        """Send screenshot to NVIDIA AI for analysis"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        Analyze this desktop screenshot and provide the exact coordinates to click to achieve: {objective}
        
        Return JSON with:
        - "click_coordinates": [x, y] - exact pixel coordinates
        - "confidence": 0-1 score
        - "element_description": what was found
        - "next_action": "click", "double_click", "right_click", "drag", "wait", "complete"
        - "reasoning": brief explanation
        
        Screen dimensions: {self.screen_width}x{self.screen_height}
        Return only valid JSON, no markdown formatting.
        """
        
        payload = {
            "model": "mistralai/mistral-small-4-119b-2603",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(self.invoke_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "error": "No JSON found in response",
                    "raw_content": content
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "click_coordinates": [self.screen_width//2, self.screen_height//2],
                "confidence": 0.0,
                "next_action": "wait"
            }
    
    def execute_click(self, coordinates: List[int], action: str = "click"):
        """Execute click action at given coordinates"""
        x, y = coordinates
        
        if action == "click":
            pyautogui.click(x, y)
        elif action == "double_click":
            pyautogui.doubleClick(x, y)
        elif action == "right_click":
            pyautogui.rightClick(x, y)
        elif action == "drag":
            pyautogui.mouseDown(x, y)
            time.sleep(0.5)
            pyautogui.moveRel(100, 0, duration=0.5)
            pyautogui.mouseUp()
            
        print(f"Executed {action} at ({x}, {y})")
    
    def find_solidworks_icon(self) -> Dict[str, Any]:
        """Find SolidWorks icon on desktop"""
        screenshot = self.take_screenshot()
        return self.analyze_screen_with_nvidia(
            screenshot, 
            "Find SolidWorks application icon or shortcut on desktop and provide exact click coordinates"
        )
    
    def run_automation_loop(self, objective: str, max_steps: int = 50):
        """Main automation loop"""
        print(f"Starting NVIDIA AI automation for: {objective}")
        
        for step in range(max_steps):
            print(f"\nStep {step + 1}")
            
            # Take screenshot
            screenshot = self.take_screenshot()
            
            # Get AI analysis
            analysis = self.analyze_screen_with_nvidia(screenshot, objective)
            
            if "error" in analysis:
                print(f"Error: {analysis['error']}")
                if analysis.get("next_action") == "wait":
                    time.sleep(2)
                    continue
                    
            # Extract coordinates and action
            coordinates = analysis.get("click_coordinates", [0, 0])
            action = analysis.get("next_action", "click")
            confidence = analysis.get("confidence", 0)
            
            print(f"AI suggests: {action} at {coordinates} (confidence: {confidence})")
            
            if confidence < 0.5:
                print("Low confidence, waiting...")
                time.sleep(3)
                continue
                
            # Execute action
            self.execute_click(coordinates, action)
            
            # Check if complete
            if action == "complete":
                print("Automation complete!")
                break
                
            time.sleep(2)
        
        print("Maximum steps reached or automation complete")

# Usage example
if __name__ == "__main__":
    # Replace with your actual NVIDIA API key
    API_KEY = "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"
    
    agent = NVIDIAAutomationAgent(API_KEY)
    
    # Example: Find and click SolidWorks
    # result = agent.find_solidworks_icon()
    # print(result)
    
    # Run full automation
    agent.run_automation_loop("Find and launch SolidWorks application from desktop")
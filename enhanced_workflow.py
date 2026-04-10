#!/usr/bin/env python3
"""
Enhanced Desktop-to-SolidWorks Assembly Automation Workflow
Complete system with coordinate storage and C++ code generation
"""
import base64
import json
import time
import os
import sqlite3
import subprocess
import platform
from typing import Dict, Any, List, Tuple, Optional
import pyautogui
import requests
from PIL import Image
import io

class EnhancedAssemblyWorkflow:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.nvidia_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.screen_width, self.screen_height = pyautogui.size()
        self.db_path = "assembly_workflow.db"
        self.coordinates_store = {}
        self.setup_database()
        self.minimize_all_windows()
        
    def setup_database(self):
        """Initialize SQLite database for storing workflow data and coordinates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Workflow steps table
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
        
        # Coordinate storage for C++ generation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coordinate_store (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_name TEXT NOT NULL,
                x_coordinate INTEGER,
                y_coordinate INTEGER,
                action_type TEXT,
                wait_time INTEGER DEFAULT 2000,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Assembly components table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assembly_components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_name TEXT NOT NULL,
                import_coordinates TEXT,
                mate_coordinates TEXT,
                assembly_order INTEGER,
                completed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def minimize_all_windows(self):
        """Minimize all windows to show clean desktop"""
        if platform.system() == "Windows":
            pyautogui.hotkey('win', 'd')
            time.sleep(2)
        elif platform.system() == "Darwin":
            pyautogui.hotkey('cmd', 'option', 'h')
            time.sleep(2)
        else:
            pyautogui.hotkey('ctrl', 'alt', 'd')
            time.sleep(2)
    
    def take_screenshot(self) -> str:
        """Take screenshot and return base64"""
        screenshot = pyautogui.screenshot()
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
    
    def store_coordinate(self, action_name: str, x: int, y: int, action_type: str, wait_time: int = 2000):
        """Store coordinate for C++ code generation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO coordinate_store (action_name, x_coordinate, y_coordinate, action_type, wait_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (action_name, x, y, action_type, wait_time))
        conn.commit()
        conn.close()
        
        # Also store in memory
        self.coordinates_store[action_name] = {
            'x': x, 'y': y, 'action': action_type, 'wait': wait_time
        }
    
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
            "action_type": "click|double_click|right_click|wait",
            "reasoning": "brief explanation"
        }}
        
        Screen: {self.screen_width}x{self.screen_height}
        """
        
        payload = {
            "model": "mistralai/mistral-small-4b-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
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
            
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "No JSON found", "click_coordinates": [0, 0], "confidence": 0}
        except Exception as e:
            return {"error": str(e), "click_coordinates": [0, 0], "confidence": 0}
    
    def execute_click(self, coordinates: List[int], action_type: str = "click"):
        """Execute click action at coordinates"""
        x, y = coordinates
        if action_type == "click":
            pyautogui.click(x, y)
        elif action_type == "double_click":
            pyautogui.doubleClick(x, y)
        elif action_type == "right_click":
            pyautogui.rightClick(x, y)
        
        print(f"Executed {action_type} at ({x}, {y})")
        return True
    
    def find_solidworks_icon(self) -> Dict[str, Any]:
        """Find SolidWorks icon on desktop"""
        screenshot = self.take_screenshot()
        return self.call_nvidia_ai(
            screenshot,
            "Find SolidWorks application icon or shortcut on desktop and provide exact click coordinates"
        )
    
    def wait_for_solidworks_open(self, timeout: int = 45) -> bool:
        """Wait for SolidWorks to fully open"""
        print("Waiting for SolidWorks to open...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            screenshot = self.take_screenshot()
            analysis = self.call_nvidia_ai(
                screenshot,
                "Check if SolidWorks is now open and ready, look for main interface"
            )
            
            if analysis.get("confidence", 0) > 0.7:
                print("SolidWorks detected as open")
                return True
            
            time.sleep(3)
        
        print("Timeout waiting for SolidWorks to open")
        return False
    
    def find_assembly_tab(self) -> Dict[str, Any]:
        """Find assembly tab/button in SolidWorks"""
        screenshot = self.take_screenshot()
        return self.call_nvidia_ai(
            screenshot,
            "Find the 'Assembly' button/tab in SolidWorks interface (not Parts, not Drawing)"
        )
    
    def wait_for_user_imports(self) -> List[str]:
        """Wait for user to manually import all components"""
        print("=== USER IMPORT PHASE ===")
        print("Please manually import all components into the assembly")
        print("1. Import each component file")
        print("2. Position components appropriately")
        print("3. Press Enter when all components are imported...")
        
        input("Press Enter to continue...")
        
        # Get component names from user
        components = []
        print("Enter component names (one per line, empty to finish):")
        
        while True:
            component = input("Component name: ").strip()
            if not component:
                break
            components.append(component)
        
        # Store components in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for idx, component in enumerate(components, 1):
            cursor.execute('''
                INSERT INTO assembly_components (component_name, assembly_order)
                VALUES (?, ?)
            ''', (component, idx))
        
        conn.commit()
        conn.close()
        
        print(f"Stored {len(components)} components for assembly")
        return components
    
    def find_and_click_component(self, component_name: str) -> Dict[str, Any]:
        """Find specific component in assembly"""
        screenshot = self.take_screenshot()
        return self.call_nvidia_ai(
            screenshot,
            f"Find the '{component_name}' component in the assembly and provide click coordinates"
        )
    
    def find_mate_button(self) -> Dict[str, Any]:
        """Find mate button for assembly"""
        screenshot = self.take_screenshot()
        return self.call_nvidia_ai(
            screenshot,
            "Find the 'Mate' or 'Assembly' button for creating mates between components"
        )
    
    def check_assembly_complete(self) -> bool:
        """Check if assembly is complete"""
        screenshot = self.take_screenshot()
        analysis = self.call_nvidia_ai(
            screenshot,
            "Check if the assembly is complete and ready, look for completion indicators"
        )
        
        return analysis.get("next_action") == "complete"
    
    def generate_cpp_code(self) -> str:
        """Generate optimized C++ code from stored coordinates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT action_name, x_coordinate, y_coordinate, action_type, wait_time 
            FROM coordinate_store ORDER BY id
        ''')
        
        coordinates = cursor.fetchall()
        conn.close()
        
        cpp_code = '''#include <iostream>
#include <windows.h>
#include <chrono>
#include <thread>

using namespace std;

class OptimizedAssemblyAutomation {
private:
    void clickAt(int x, int y) {
        SetCursorPos(x, y);
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
    }
    
    void doubleClickAt(int x, int y) {
        SetCursorPos(x, y);
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
    }
    
    void rightClickAt(int x, int y) {
        SetCursorPos(x, y);
        mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0);
        mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0);
    }
    
    void waitMs(int milliseconds) {
        this_thread::sleep_for(chrono::milliseconds(milliseconds));
    }

public:
    void runAssemblyWorkflow() {
        cout << "Starting optimized assembly workflow..." << endl;
        
'''
        
        for action_name, x, y, action_type, wait_time in coordinates:
            cpp_code += f'        cout << "{action_name}" << endl;\n'
            cpp_code += f'        waitMs({wait_time});\n'
            
            if action_type == "click":
                cpp_code += f'        clickAt({x}, {y});\n'
            elif action_type == "double_click":
                cpp_code += f'        doubleClickAt({x}, {y});\n'
            elif action_type == "right_click":
                cpp_code += f'        rightClickAt({x}, {y});\n'
            
            cpp_code += f'        waitMs(1000);\n\n'
        
        cpp_code += '''        cout << "Assembly workflow completed!" << endl;
    }
};

int main() {
    OptimizedAssemblyAutomation automation;
    automation.runAssemblyWorkflow();
    return 0;
}'''
        
        # Write C++ file
        with open("optimized_assembly_automation.cpp", "w") as f:
            f.write(cpp_code)
        
        return cpp_code
    
    def run_complete_workflow(self):
        """Execute complete desktop-to-assembly workflow"""
        print("=== Enhanced Desktop-to-SolidWorks Assembly Automation ===")
        
        # Step 1: Start from desktop (already minimized)
        print("Step 1: Starting from clean desktop...")
        
        # Step 2: Find and click SolidWorks icon
        print("Step 2: Finding SolidWorks icon...")
        sw_result = self.find_solidworks_icon()
        if sw_result.get("confidence", 0) > 0.7:
            coords = sw_result["click_coordinates"]
            self.execute_click(coords)
            self.store_coordinate("click_solidworks_icon", coords[0], coords[1], "click", 3000)
            print(f"Clicked SolidWorks icon at {coords}")
        else:
            print("Could not find SolidWorks icon")
            return False
        
        # Step 3: Wait for SolidWorks to open
        if not self.wait_for_solidworks_open():
            return False
        
        # Step 4: Find and click Assembly tab
        print("Step 4: Finding Assembly tab...")
        assembly_result = self.find_assembly_tab()
        if assembly_result.get("confidence", 0) > 0.7:
            coords = assembly_result["click_coordinates"]
            self.execute_click(coords)
            self.store_coordinate("click_assembly_tab", coords[0], coords[1], "click", 2000)
            print(f"Clicked Assembly tab at {coords}")
        
        # Step 5: User import phase
        components = self.wait_for_user_imports()
        
        # Step 6: Assembly automation phase
        print("=== ASSEMBLY AUTOMATION PHASE ===")
        for component in components:
            print(f"Processing component: {component}")
            
            # Find component
            comp_result = self.find_and_click_component(component)
            if comp_result.get("confidence", 0) > 0.7:
                coords = comp_result["click_coordinates"]
                self.execute_click(coords)
                self.store_coordinate(f"select_{component}", coords[0], coords[1], "click", 1500)
            
            # Find mate button
            mate_result = self.find_mate_button()
            if mate_result.get("confidence", 0) > 0.7:
                coords = mate_result["click_coordinates"]
                self.execute_click(coords)
                self.store_coordinate("click_mate_button", coords[0], coords[1], "click", 2000)
        
        # Step 7: Check completion
        if self.check_assembly_complete():
            print("Assembly completed successfully!")
            
            # Step 8: Generate C++ code
            cpp_code = self.generate_cpp_code()
            print("Generated optimized C++ code: optimized_assembly_automation.cpp")
            
            return True
        
        return False

if __name__ == "__main__":
    # Replace with your actual NVIDIA API key
    API_KEY = "your_nvidia_api_key_here"
    
    workflow = EnhancedAssemblyWorkflow(API_KEY)
    workflow.run_complete_workflow()
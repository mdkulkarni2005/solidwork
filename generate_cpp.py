#!/usr/bin/env python3
"""
C++ Code Generator for Optimized Assembly Automation
Reads stored coordinates and generates production-ready C++ code
"""
import sqlite3
import os
from typing import List, Tuple

class CppCodeGenerator:
    def __init__(self, db_path: str = "assembly_workflow.db"):
        self.db_path = db_path
        
    def generate_optimized_cpp(self) -> str:
        """Generate complete C++ automation code"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all stored coordinates
        cursor.execute('''
            SELECT action_name, x_coordinate, y_coordinate, action_type, wait_time 
            FROM coordinate_store ORDER BY id
        ''')
        
        coordinates = cursor.fetchall()
        conn.close()
        
        if not coordinates:
            return "// No coordinates stored yet. Run the Python workflow first."
        
        cpp_code = self._generate_cpp_header()
        cpp_code += self._generate_coordinate_struct(coordinates)
        cpp_code += self._generate_automation_class(coordinates)
        cpp_code += self._generate_main_function()
        
        return cpp_code
    
    def _generate_cpp_header(self) -> str:
        return '''#include <iostream>
#include <windows.h>
#include <chrono>
#include <thread>
#include <vector>
#include <string>

using namespace std;
using namespace std::chrono;

// Windows API helper functions
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

'''
    
    def _generate_coordinate_struct(self, coordinates: List[Tuple]) -> str:
        struct_code = '''
struct AutomationStep {
    string action_name;
    int x;
    int y;
    string action_type;
    int wait_time;
};

'''
        
        # Generate the coordinate array
        struct_code += 'const vector<AutomationStep> assembly_steps = {\n'
        
        for action_name, x, y, action_type, wait_time in coordinates:
            struct_code += f'    {{"{action_name}", {x}, {y}, "{action_type}", {wait_time}}},\n'
        
        struct_code += '};\n\n'
        return struct_code
    
    def _generate_automation_class(self, coordinates: List[Tuple]) -> str:
        return '''
class OptimizedAssemblyAutomation {
private:
    int screen_width;
    int screen_height;
    
public:
    OptimizedAssemblyAutomation() {
        // Get screen dimensions
        screen_width = GetSystemMetrics(SM_CXSCREEN);
        screen_height = GetSystemMetrics(SM_CYSCREEN);
    }
    
    void log(const string& message) {
        cout << "[LOG] " << message << endl;
    }
    
    void executeStep(const AutomationStep& step) {
        log("Executing: " + step.action_name);
        
        // Wait before action
        waitMs(step.wait_time);
        
        // Execute action
        if (step.action_type == "click") {
            clickAt(step.x, step.y);
        } else if (step.action_type == "double_click") {
            doubleClickAt(step.x, step.y);
        } else if (step.action_type == "right_click") {
            rightClickAt(step.x, step.y);
        }
        
        // Small delay after action
        waitMs(1000);
    }
    
    void runAssemblyWorkflow() {
        log("Starting optimized assembly workflow...");
        log("Screen dimensions: " + to_string(screen_width) + "x" + to_string(screen_height));
        
        for (const auto& step : assembly_steps) {
            executeStep(step);
        }
        
        log("Assembly workflow completed successfully!");
    }
    
    void runWithVerification() {
        log("Starting assembly with verification...");
        
        for (const auto& step : assembly_steps) {
            // Verify coordinates are within screen bounds
            if (step.x < 0 || step.x > screen_width || step.y < 0 || step.y > screen_height) {
                log("WARNING: Coordinates out of bounds for " + step.action_name);
                continue;
            }
            
            executeStep(step);
        }
        
        log("Assembly completed with verification!");
    }
};

'''
    
    def _generate_main_function(self) -> str:
        return '''
int main() {
    cout << "=== Optimized Assembly Automation ===" << endl;
    cout << "Using pre-calculated coordinates from Python workflow" << endl;
    cout << "No AI calls required - pure optimized execution" << endl << endl;
    
    OptimizedAssemblyAutomation automation;
    
    try {
        automation.runAssemblyWorkflow();
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
    
    cout << endl << "Press Enter to exit...";
    cin.get();
    return 0;
}'''
    
    def save_cpp_file(self, filename: str = "optimized_assembly_automation.cpp") -> bool:
        """Save generated C++ code to file"""
        try:
            cpp_code = self.generate_optimized_cpp()
            with open(filename, "w") as f:
                f.write(cpp_code)
            print(f"Generated C++ code saved to: {filename}")
            return True
        except Exception as e:
            print(f"Error generating C++ code: {e}")
            return False
    
    def create_cmake_file(self) -> bool:
        """Create CMakeLists.txt for building"""
        cmake_content = '''cmake_minimum_required(VERSION 3.10)
project(AssemblyAutomation)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Threads REQUIRED)

# Add executable
add_executable(assembly_automation optimized_assembly_automation.cpp)

# Link libraries
target_link_libraries(assembly_automation ${CMAKE_THREAD_LIBS_INIT})

# Windows-specific settings
if(WIN32)
    target_link_libraries(assembly_automation user32)
endif()

# Compiler flags
if(MSVC)
    target_compile_options(assembly_automation PRIVATE /W4)
else()
    target_compile_options(assembly_automation PRIVATE -Wall -Wextra)
endif()
'''
        
        try:
            with open("CMakeLists.txt", "w") as f:
                f.write(cmake_content)
            print("Created CMakeLists.txt")
            return True
        except Exception as e:
            print(f"Error creating CMakeLists.txt: {e}")
            return False

if __name__ == "__main__":
    generator = CppCodeGenerator()
    
    if generator.save_cpp_file():
        print("C++ code generation successful!")
        
        if generator.create_cmake_file():
            print("Build files created successfully!")
            print("\nTo build:")
            print("  mkdir build && cd build")
            print("  cmake ..")
            print("  cmake --build . --config Release")
    else:
        print("C++ code generation failed")
#!/usr/bin/env python3
"""
Main runner for the complete desktop-to-SolidWorks assembly workflow
"""
import sys
import os
import subprocess
from enhanced_workflow import EnhancedAssemblyWorkflow
from generate_cpp import CppCodeGenerator

def main():
    """Main entry point for the complete workflow"""
    print("=== Desktop-to-SolidWorks Assembly Automation ===")
    print("Complete workflow with coordinate storage and C++ generation")
    print()
    
    # Check for API key
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        api_key = input("Enter your NVIDIA API key: ").strip()
        if not api_key:
            print("Error: NVIDIA API key is required")
            sys.exit(1)
    
    try:
        # Initialize workflow
        workflow = EnhancedAssemblyWorkflow(api_key)
        
        print("Starting complete workflow...")
        print("1. Python workflow will run and store coordinates")
        print("2. C++ code will be generated automatically")
        print("3. You can then use the C++ version for faster execution")
        print()
        
        # Run the complete workflow
        success = workflow.run_complete_workflow()
        
        if success:
            print("\n=== Workflow Complete ===")
            print("Python workflow finished successfully!")
            
            # Generate C++ code
            print("\nGenerating optimized C++ code...")
            generator = CppCodeGenerator()
            
            if generator.save_cpp_file():
                print("✓ C++ code generated: optimized_assembly_automation.cpp")
                
                if generator.create_cmake_file():
                    print("✓ CMakeLists.txt created")
                    
                    print("\n=== Next Steps ===")
                    print("1. Build C++ version:")
                    print("   mkdir build && cd build")
                    print("   cmake ..")
                    print("   cmake --build . --config Release")
                    print("\n2. Run C++ version:")
                    print("   ./assembly_automation")
                    print("\n3. C++ version uses stored coordinates - no AI calls needed!")
                    
                else:
                    print("✗ Failed to create CMakeLists.txt")
            else:
                print("✗ Failed to generate C++ code")
        else:
            print("✗ Workflow failed")
            
    except KeyboardInterrupt:
        print("\nWorkflow interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
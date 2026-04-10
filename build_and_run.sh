#!/bin/bash

# Build and run the C++ assembly automation system

echo "Building C++ Assembly Automation System..."

# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build . --config Release

# Check if build successful
if [ -f "assembly_automation" ] || [ -f "Release/assembly_automation.exe" ]; then
    echo "Build successful!"
    echo "Running assembly automation..."
    
    # Run the program
    if [ -f "assembly_automation" ]; then
        ./assembly_automation
    elif [ -f "Release/assembly_automation.exe" ]; then
        ./Release/assembly_automation.exe
    fi
else
    echo "Build failed! Check OpenCV installation."
    echo "Install OpenCV: sudo apt-get install libopencv-dev (Linux) or use vcpkg (Windows)"
fi

cd ..
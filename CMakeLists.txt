cmake_minimum_required(VERSION 3.16)
project(SolidWorksAssemblyAutomation)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenCV
find_package(OpenCV REQUIRED)

# Add executable
add_executable(assembly_automation assembly_automation.cpp)

# Link OpenCV
target_link_libraries(assembly_automation ${OpenCV_LIBS})

# Windows-specific settings
if(WIN32)
    target_link_libraries(assembly_automation user32 gdi32)
endif()

# Compiler flags
if(MSVC)
    target_compile_options(assembly_automation PRIVATE /W4)
else()
    target_compile_options(assembly_automation PRIVATE -Wall -Wextra)
endif()
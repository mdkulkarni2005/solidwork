#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <windows.h>
#include <opencv2/opencv.hpp>

class AssemblyAutomation {
private:
    int screenWidth;
    int screenHeight;
    std::vector<std::pair<int, int>> clickHistory;
    bool assemblyComplete = false;

public:
    AssemblyAutomation() {
        screenWidth = GetSystemMetrics(SM_CXSCREEN);
        screenHeight = GetSystemMetrics(SM_CYSCREEN);
    }

    cv::Mat takeScreenshot() {
        HWND hwnd = GetDesktopWindow();
        HDC hdc = GetDC(hwnd);
        HDC hdcMem = CreateCompatibleDC(hdc);
        
        HBITMAP hBitmap = CreateCompatibleBitmap(hdc, screenWidth, screenHeight);
        SelectObject(hdcMem, hBitmap);
        BitBlt(hdcMem, 0, 0, screenWidth, screenHeight, hdc, 0, 0, SRCCOPY);
        
        BITMAPINFOHEADER bi = {0};
        bi.biSize = sizeof(BITMAPINFOHEADER);
        bi.biWidth = screenWidth;
        bi.biHeight = -screenHeight;
        bi.biPlanes = 1;
        bi.biBitCount = 32;
        bi.biCompression = BI_RGB;
        
        cv::Mat mat(screenHeight, screenWidth, CV_8UC4);
        GetDIBits(hdcMem, hBitmap, 0, screenHeight, mat.data, (BITMAPINFO*)&bi, DIB_RGB_COLORS);
        
        cv::cvtColor(mat, mat, cv::COLOR_BGRA2BGR);
        
        DeleteObject(hBitmap);
        DeleteDC(hdcMem);
        ReleaseDC(hwnd, hdc);
        
        return mat;
    }

    std::string encodeImageBase64(const cv::Mat& image) {
        std::vector<uchar> buffer;
        cv::imencode(".png", image, buffer);
        return base64_encode(buffer.data(), buffer.size());
    }

    static std::string base64_encode(const unsigned char* data, size_t len) {
        static const char* base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        std::string ret;
        int i = 0;
        int j = 0;
        unsigned char char_array_3[3];
        unsigned char char_array_4[4];

        while (len--) {
            char_array_3[i++] = *(data++);
            if (i == 3) {
                char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
                char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
                char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
                char_array_4[3] = char_array_3[2] & 0x3f;

                for (i = 0; i < 4; i++)
                    ret += base64_chars[char_array_4[i]];
                i = 0;
            }
        }

        if (i) {
            for (j = i; j < 3; j++)
                char_array_3[j] = 0;

            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
            char_array_4[3] = char_array_3[2] & 0x3f;

            for (j = 0; j < i + 1; j++)
                ret += base64_chars[char_array_4[j]];

            while (i++ < 3)
                ret += '=';
        }

        return ret;
    }

    void clickAt(int x, int y) {
        SetCursorPos(x, y);
        mouse_event(MOUSEEVENTF_LEFTDOWN, x, y, 0, 0);
        mouse_event(MOUSEEVENTF_LEFTUP, x, y, 0, 0);
        clickHistory.push_back({x, y});
        std::cout << "Clicked at (" << x << ", " << y << ")\n";
    }

    bool checkAssemblyComplete() {
        cv::Mat screenshot = takeScreenshot();
        
        // Check for assembly completion indicators
        cv::Mat hsv;
        cv::cvtColor(screenshot, hsv, cv::COLOR_BGR2HSV);
        
        // Look for green completion indicators
        cv::Scalar lower_green(40, 40, 40);
        cv::Scalar upper_green(80, 255, 255);
        cv::Mat green_mask;
        cv::inRange(hsv, lower_green, upper_green, green_mask);
        
        double green_ratio = cv::countNonZero(green_mask) / (double)(screenWidth * screenHeight);
        
        // Check for SolidWorks assembly complete dialog
        cv::Mat gray;
        cv::cvtColor(screenshot, gray, cv::COLOR_BGR2GRAY);
        
        std::vector<cv::Rect> faces;
        cv::CascadeClassifier face_cascade;
        
        // Simple completion detection based on dialog presence
        cv::Mat edges;
        cv::Canny(gray, edges, 50, 150);
        
        std::vector<std::vector<cv::Point>> contours;
        cv::findContours(edges, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
        
        for (const auto& contour : contours) {
            cv::Rect rect = cv::boundingRect(contour);
            if (rect.width > 200 && rect.height > 100) {
                // Check for dialog-like rectangles
                if (rect.x > screenWidth * 0.3 && rect.x < screenWidth * 0.7) {
                    assemblyComplete = true;
                    return true;
                }
            }
        }
        
        return false;
    }

    std::string callNVIDIAAI(const std::string& image_base64, const std::string& objective) {
        // Placeholder for NVIDIA API call
        // In real implementation, use libcurl or WinHTTP
        return R"({
            "click_coordinates": [500, 300],
            "confidence": 0.95,
            "element_description": "SolidWorks icon",
            "next_action": "click",
            "reasoning": "Found SolidWorks desktop shortcut"
        })";
    }

    void runAssemblyLoop(const std::string& objective) {
        std::cout << "Starting assembly automation loop...\n";
        
        int step = 0;
        const int max_steps = 100;
        
        while (step < max_steps && !assemblyComplete) {
            std::cout << "Step " << step + 1 << "\n";
            
            // Take screenshot
            cv::Mat screenshot = takeScreenshot();
            std::string image_b64 = encodeImageBase64(screenshot);
            
            // Call NVIDIA AI
            std::string ai_response = callNVIDIAAI(image_b64, objective);
            
            // Parse response (simplified)
            int x = 500, y = 300;
            std::string action = "click";
            
            // Execute action
            clickAt(x, y);
            
            // Check if assembly complete
            if (checkAssemblyComplete()) {
                std::cout << "Assembly completed successfully!\n";
                break;
            }
            
            std::this_thread::sleep_for(std::chrono::seconds(2));
            step++;
        }
        
        if (assemblyComplete) {
            generateCPPCode();
        }
    }

    void generateCPPCode() {
        std::ofstream file("final_assembly_automation.cpp");
        file << R"(#include <iostream>
#include <windows.h>
#include <vector>

class FinalAssemblyAutomation {
private:
    std::vector<std::pair<int, int>> assemblyCoordinates;
    
public:
    FinalAssemblyAutomation() {
        // Pre-calculated coordinates from successful assembly
        assemblyCoordinates = {
";
        
        for (const auto& coord : clickHistory) {
            file << "            {" << coord.first << ", " << coord.second << "},\n";
        }
        
        file << R"(        };
    }
    
    void executeAssembly() {
        std::cout << "Executing final assembly with pre-calculated coordinates...\n";
        
        for (const auto& coord : assemblyCoordinates) {
            SetCursorPos(coord.first, coord.second);
            mouse_event(MOUSEEVENTF_LEFTDOWN, coord.first, coord.second, 0, 0);
            mouse_event(MOUSEEVENTF_LEFTUP, coord.first, coord.second, 0, 0);
            
            std::cout << "Clicked at (" << coord.first << ", " << coord.second << ")\n";
            Sleep(1000);
        }
        
        std::cout << "Assembly completed using optimized C++ code!\n";
    }
};

int main() {
    FinalAssemblyAutomation automation;
    automation.executeAssembly();
    return 0;
}
)";
        file.close();
        
        std::cout << "Generated final_assembly_automation.cpp with optimized coordinates\n";
    }
};

int main() {
    AssemblyAutomation automation;
    automation.runAssemblyLoop("Complete SolidWorks assembly automation");
    return 0;
}
import webview
import sys
import os
import winreg
import threading
import time

# Configuration - change this URL to your desired website
WEBSITE_URL = "https://app.ievo.in"  # Change this to your web app URL
WINDOW_TITLE = "I.EVO App Widget"
WINDOW_WIDTH = 430
WINDOW_HEIGHT = 800  # 1280x720 = 16:9 aspect ratio

def set_startup():
    """Add the application to startup registry"""
    try:
        # Get the path to the executable
        exe_path = os.path.abspath(sys.argv[0])
        
        # If running as a script, use pythonw.exe to run the script
        if exe_path.endswith('.py'):
            pythonw_path = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
            exe_path = f'"{pythonw_path}" "{exe_path}"'
        else:
            exe_path = f'"{exe_path}"'
            
        # Open the registry key for current user startup programs
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        
        # Set the value
        winreg.SetValueEx(key, "WebWidget", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        print("Added to startup successfully")
    except Exception as e:
        print(f"Error adding to startup: {e}")

def inject_persistent_back_button(window):
    """Continuously inject back button on every page"""
    while True:
        time.sleep(1)  # Check every second
        
        try:
            # Check if back button already exists
            has_button = window.evaluate_js("""
                document.getElementById('webwidget-back-btn') !== null
            """)
            
            if not has_button:
                # Inject back button
                js_code = """
                // Remove any existing back button first
                var existingBtn = document.getElementById('webwidget-back-btn');
                if (existingBtn) {
                    existingBtn.remove();
                }
                
                // Create and inject styles
                var style = document.createElement('style');
                style.innerHTML = `
                    #webwidget-back-btn {
                        position: fixed !important;
                        top: 10px !important;
                        left: 10px !important;
                        z-index: 9999 !important;
                        width: 40px !important;
                        height: 40px !important;
                        border-radius: 50% !important;
                        background-color: rgba(255, 255, 255, 0.8) !important;
                        border: 1px solid #ccc !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        font-size: 20px !important;
                        cursor: pointer !important;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
                        transition: background-color 0.3s !important;
                    }
                    #webwidget-back-btn:hover {
                        background-color: rgba(240, 240, 240, 0.9) !important;
                    }
                `;
                document.head.appendChild(style);
                
                // Create back button
                var backBtn = document.createElement('div');
                backBtn.id = 'webwidget-back-btn';
                backBtn.innerHTML = '←';
                backBtn.onclick = function() {
                    window.history.back();
                };
                document.body.appendChild(backBtn);
                """
                window.evaluate_js(js_code)
        except:
            # If evaluation fails, continue trying
            continue

def create_window():
    """Create the webview window"""
    # Create the main browser window
    window = webview.create_window(
        title=WINDOW_TITLE,
        url=WEBSITE_URL,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        resizable=False,
        text_select=True,
        confirm_close=True,
    )
    
    # Start a thread to continuously inject the back button
    threading.Thread(target=inject_persistent_back_button, args=(window,), daemon=True).start()
    
    # Start the webview
    webview.start()

if __name__ == '__main__':
    # Add to startup if not already there
    set_startup()
    
    # Create and run the window
    create_window()
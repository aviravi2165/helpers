import webview
import sys
import os
import winreg
import threading
import time
import json
from pathlib import Path

# Configuration - change this URL to your desired website
WEBSITE_URL = "https://app.ievo.in"  # Change this to your web app URL
WINDOW_TITLE = "I.EVO App Widget"
WINDOW_WIDTH = 430
WINDOW_HEIGHT = 800

# Persistent storage paths
APP_DATA_DIR = Path(os.getenv('APPDATA')) / 'IEvoWidget'
USER_DATA_DIR = APP_DATA_DIR / 'UserData'
CONFIG_FILE = APP_DATA_DIR / 'config.json'

# Create application data directory if it doesn't exist
os.makedirs(USER_DATA_DIR, exist_ok=True)

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
        winreg.SetValueEx(key, "IEvoWidget", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        print("Added to startup successfully")
    except Exception as e:
        print(f"Error adding to startup: {e}")

def save_config():
    """Save configuration to file"""
    config = {
        'website_url': WEBSITE_URL,
        'window_width': WINDOW_WIDTH,
        'window_height': WINDOW_HEIGHT,
        'last_updated': time.time()
    }
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print("Configuration saved successfully")
    except Exception as e:
        print(f"Error saving config: {e}")

def load_config():
    """Load configuration from file"""
    global WEBSITE_URL, WINDOW_WIDTH, WINDOW_HEIGHT
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                WEBSITE_URL = config.get('website_url', WEBSITE_URL)
                WINDOW_WIDTH = config.get('window_width', WINDOW_WIDTH)
                WINDOW_HEIGHT = config.get('window_height', WINDOW_HEIGHT)
                print("Configuration loaded successfully")
        except Exception as e:
            print(f"Error loading config: {e}")

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
                        top: 8px !important;
                        right: 64px !important;
                        z-index: 9999 !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        cursor: pointer !important;
                        width: 40px !important;
                        height: 40px !important;
                        border-radius: 50% !important;
                        color: #f4f6f8 !important;
                        background-color: #bdbdbd !important;                        
                        transition: background-color 0.3s !important;
                    }
                    #webwidget-back-btn:hover {
                        background-color: #616161 !important;
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
    """Create the webview window with persistent cookies"""
    # Load configuration
    load_config()
    
    # Set environment variables for persistent storage
    # This is the correct way to enable persistent cookies in pywebview
    os.environ['WEBVIEW_PERSISTENT_STORAGE'] = str(USER_DATA_DIR)
    
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
    
    # Save configuration when window is closed
    def on_closed():
        save_config()
        print("Application closed. Cookies and configuration saved persistently.")
    
    # Set closed event handler
    try:
        window.events.closed += on_closed
    except:
        # Fallback if events are not supported
        pass
    
    # Start a thread to continuously inject the back button
    threading.Thread(target=inject_persistent_back_button, args=(window,), daemon=True).start()
    
    # Start the webview
    webview.start()

if __name__ == '__main__':
    # Add to startup if not already there
    set_startup()
    
    # Create and run the window
    create_window()
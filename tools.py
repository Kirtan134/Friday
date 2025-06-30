import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
import pyautogui
import cv2
import numpy as np
from PIL import Image
import base64
import io
import time
import subprocess
import shutil
import psutil
from pathlib import Path
import json
from datetime import datetime
import sys
import winreg

# Disable pyautogui failsafe for automation
pyautogui.FAILSAFE = False

# Memory storage file
MEMORY_FILE = "friday_memory.json"

class MemoryManager:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.memory = self.load_memory()

    def load_memory(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            return {"conversations": [], "user_preferences": {}, "tasks": [], "reminders": []}
        except Exception as e:
            logging.error(f"Error loading memory: {e}")
            return {"conversations": [], "user_preferences": {}, "tasks": [], "reminders": []}

    def save_memory(self):
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving memory: {e}")

    def add_conversation(self, user_input, assistant_response):
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_response
        }
        self.memory["conversations"].append(conversation)
        # Keep only last 50 conversations
        if len(self.memory["conversations"]) > 50:
            self.memory["conversations"] = self.memory["conversations"][-50:]
        self.save_memory()

    def set_preference(self, key, value):
        self.memory["user_preferences"][key] = value
        self.save_memory()

    def get_preference(self, key):
        return self.memory["user_preferences"].get(key)

    def add_task(self, task):
        self.memory["tasks"].append({
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "completed": False
        })
        self.save_memory()

    def add_reminder(self, reminder, date_time=None):
        self.memory["reminders"].append({
            "reminder": reminder,
            "datetime": date_time,
            "created": datetime.now().isoformat()
        })
        self.save_memory()

# Global memory manager
memory_manager = MemoryManager()

@function_tool()
async def remember_information(
    context: RunContext,
    key: str,
    value: str
) -> str:
    """
    Remember user preferences and information for future reference.

    Args:
        key: The key to store the information under
        value: The value to remember
    """
    try:
        memory_manager.set_preference(key, value)
        return f"I'll remember that {key}: {value}"
    except Exception as e:
        return f"Failed to remember information: {str(e)}"

@function_tool()
async def recall_information(
    context: RunContext,
    key: str
) -> str:
    """
    Recall previously stored information.

    Args:
        key: The key to retrieve information for
    """
    try:
        value = memory_manager.get_preference(key)
        if value:
            return f"I remember that {key}: {value}"
        else:
            return f"I don't have any information stored for {key}"
    except Exception as e:
        return f"Failed to recall information: {str(e)}"

@function_tool()
async def add_task_to_memory(
    context: RunContext,
    task: str
) -> str:
    """
    Add a task to memory for tracking.

    Args:
        task: The task to remember
    """
    try:
        memory_manager.add_task(task)
        return f"Task added to memory: {task}"
    except Exception as e:
        return f"Failed to add task: {str(e)}"

@function_tool()
async def get_weather(
    context: RunContext,  # type: ignore
    city: str) -> str:
    """
    Get the current weather for a given city.
    """
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}."

@function_tool()
async def search_web(
    context: RunContext,  # type: ignore
    query: str) -> str:
    """
    Search the web using DuckDuckGo.
    """
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web for '{query}'."

@function_tool()
async def send_email(
    context: RunContext,  # type: ignore
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None
) -> str:
    """
    Send an email through Gmail.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        message: Email body content
        cc_email: Optional CC email address
    """
    try:
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Get credentials from environment variables
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # Use App Password, not regular password

        if not gmail_user or not gmail_password:
            logging.error("Gmail credentials not found in environment variables")
            return "Email sending failed: Gmail credentials not configured."

        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add CC if provided
        recipients = [to_email]
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)

        # Attach message body
        msg.attach(MIMEText(message, 'plain'))

        # Connect to Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(gmail_user, gmail_password)

        # Send email
        text = msg.as_string()
        server.sendmail(gmail_user, recipients, text)
        server.quit()

        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"

    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Email sending failed: Authentication error. Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An error occurred while sending email: {str(e)}"

@function_tool()
async def capture_screen(
    context: RunContext,  # type: ignore
    save_path: Optional[str] = None,
    region: Optional[str] = None
) -> str:
    """
    Capture a screenshot of the current screen.

    Args:
        save_path: Optional path to save the screenshot (e.g., 'screenshot.png')
        region: Optional region to capture in format 'x,y,width,height' (e.g., '100,100,800,600')
    """
    try:
        # Parse region if provided
        bbox = None
        if region:
            try:
                x, y, width, height = map(int, region.split(','))
                bbox = (x, y, width, height)
            except ValueError:
                logging.error(f"Invalid region format: {region}. Use 'x,y,width,height'")
                return "Invalid region format. Use 'x,y,width,height' (e.g., '100,100,800,600')"

        # Capture screenshot
        if bbox:
            screenshot = pyautogui.screenshot(region=bbox)
            logging.info(f"Screenshot captured from region {region}")
        else:
            screenshot = pyautogui.screenshot()
            logging.info("Full screen screenshot captured")

        # Save screenshot if path provided
        if save_path:
            try:
                screenshot.save(save_path)
                logging.info(f"Screenshot saved to {save_path}")
                return f"Screenshot captured and saved to {save_path}"
            except Exception as e:
                logging.error(f"Failed to save screenshot: {e}")
                return f"Screenshot captured but failed to save: {str(e)}"
        else:
            # Convert to base64 for transmission
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            logging.info("Screenshot captured and converted to base64")
            return f"Screenshot captured successfully. Image data available."

    except Exception as e:
        logging.error(f"Error capturing screenshot: {e}")
        return f"Failed to capture screenshot: {str(e)}"

@function_tool()
async def get_screen_info(
    context: RunContext  # type: ignore
) -> str:
    """
    Get information about the current screen resolution and setup.
    """
    try:
        # Get screen size
        screen_size = pyautogui.size()

        # Get mouse position
        mouse_pos = pyautogui.position()

        info = f"""Screen Information:
- Resolution: {screen_size.width} x {screen_size.height}
- Current mouse position
- Screen area: {screen_size.width * screen_size.height} pixels"""

        logging.info("Screen information retrieved")
        return info

    except Exception as e:
        logging.error(f"Error getting screen info: {e}")
        return f"Failed to get screen information: {str(e)}"

@function_tool()
async def find_on_screen(
    context: RunContext,  # type: ignore
    image_path: str,
    confidence: float = 0.8
) -> str:
    """
    Find an image on the screen using template matching.

    Args:
        image_path: Path to the template image to find
        confidence: Confidence threshold (0.0 to 1.0)
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return f"Template image not found: {image_path}"

        # Find the image on screen
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)

        if location:
            center = pyautogui.center(location)
            result = f"Image found at position: {center.x}, {center.y} (region: {location})"
            logging.info(f"Image found: {result}")
            return result
        else:
            logging.info(f"Image not found on screen: {image_path}")
            return f"Image not found on screen with confidence {confidence}"

    except Exception as e:
        logging.error(f"Error finding image on screen: {e}")
        return f"Failed to find image on screen: {str(e)}"

@function_tool()
async def click_on_screen(
    context: RunContext,  # type: ignore
    x: int,
    y: int,
    button: str = "left",
    clicks: int = 1
) -> str:
    """
    Click at a specific position on the screen.

    Args:
        x: X coordinate to click
        y: Y coordinate to click
        button: Mouse button to use ('left', 'right', 'middle')
        clicks: Number of clicks (1 for single, 2 for double)
    """
    try:
        # Validate coordinates
        screen_size = pyautogui.size()
        if x < 0 or x > screen_size.width or y < 0 or y > screen_size.height:
            return f"Invalid coordinates: ({x}, {y}). Screen size is {screen_size.width}x{screen_size.height}"

        # Perform click
        pyautogui.click(x, y, clicks=clicks, button=button)

        result = f"Clicked at ({x}, {y}) with {button} button ({clicks} click{'s' if clicks != 1 else ''})"
        logging.info(result)
        return result

    except Exception as e:
        logging.error(f"Error clicking on screen: {e}")
        return f"Failed to click on screen: {str(e)}"

@function_tool()
async def type_text(
    context: RunContext,  # type: ignore
    text: str,
    interval: float = 0.0
) -> str:
    """
    Type text at the current cursor position.

    Args:
        text: Text to type
        interval: Interval between keystrokes in seconds
    """
    try:
        pyautogui.typewrite(text, interval=interval)

        result = f"Typed text: '{text}'"
        logging.info(result)
        return result

    except Exception as e:
        logging.error(f"Error typing text: {e}")
        return f"Failed to type text: {str(e)}"

@function_tool()
async def press_key_combination(
    context: RunContext,  # type: ignore
    keys: str
) -> str:
    """
    Press a key combination (keyboard shortcut).

    Args:
        keys: Key combination separated by '+' (e.g., 'ctrl+c', 'alt+tab', 'win+r')
    """
    try:
        # Parse and press key combination
        key_list = [key.strip() for key in keys.split('+')]
        pyautogui.hotkey(*key_list)

        result = f"Pressed key combination: {keys}"
        logging.info(result)
        return result

    except Exception as e:
        logging.error(f"Error pressing key combination: {e}")
        return f"Failed to press key combination: {str(e)}"

@function_tool()
async def open_application(
    context: RunContext,  # type: ignore
    app_name: str,
    app_path: Optional[str] = None
) -> str:
    """
    Open an application by name or path with enhanced Windows support.

    Args:
        app_name: Application name (e.g., 'notepad', 'chrome', 'code', 'calculator', 'explorer')
        app_path: Optional full path to application executable
    """
    try:
        # Common application mappings for Windows
        app_mappings = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'code': 'code.exe',
            'vscode': 'code.exe',
            'discord': 'Discord.exe',
            'teams': 'Teams.exe',
            'spotify': 'Spotify.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            'outlook': 'outlook.exe'
        }

        if app_path and os.path.exists(app_path):
            # Open from specific path
            subprocess.Popen([app_path], shell=True)
            result = f"Opened application from path: {app_path}"
        else:
            app_lower = app_name.lower()

            # Try mapped executable first
            if app_lower in app_mappings:
                executable = app_mappings[app_lower]
                try:
                    subprocess.Popen([executable], shell=True)
                    result = f"Opened {app_name} using {executable}"
                except:
                    # Fallback to start command
                    subprocess.Popen(['start', '', app_name], shell=True)
                    result = f"Opened application: {app_name}"
            else:
                # Try multiple methods
                methods = [
                    lambda: subprocess.Popen([app_name], shell=True),
                    lambda: subprocess.Popen(['start', '', app_name], shell=True),
                    lambda: subprocess.Popen(f'start {app_name}', shell=True),
                    lambda: os.system(f'start {app_name}')
                ]

                success = False
                for method in methods:
                    try:
                        method()
                        success = True
                        break
                    except:
                        continue

                if success:
                    result = f"Opened application: {app_name}"
                else:
                    result = f"Could not open application: {app_name}. Try providing the full path."

        logging.info(result)
        return result

    except Exception as e:
        logging.error(f"Error opening application: {e}")
        return f"Failed to open application: {str(e)}"

@function_tool()
async def close_application(
    context: RunContext,  # type: ignore
    process_name: str
) -> str:
    """
    Close an application by process name.

    Args:
        process_name: Process name to close (e.g., 'notepad.exe', 'chrome.exe')
    """
    try:
        closed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if closed_count > 0:
            result = f"Closed {closed_count} instance(s) of {process_name}"
        else:
            result = f"No running instances of {process_name} found"

        logging.info(result)
        return result

    except Exception as e:
        logging.error(f"Error closing application: {e}")
        return f"Failed to close application: {str(e)}"

@function_tool()
async def get_running_processes(
    context: RunContext  # type: ignore
) -> str:
    """
    Get a list of currently running processes.
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': round(proc.info['cpu_percent'], 1),
                    'memory': round(proc.info['memory_percent'], 1)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu'], reverse=True)

        # Return top 10 processes
        top_processes = processes[:10]
        result = "Top 10 running processes:\n"
        for proc in top_processes:
            result += f"- {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu']}%, Memory: {proc['memory']}%\n"

        logging.info("Running processes retrieved")
        return result

    except Exception as e:
        logging.error(f"Error getting running processes: {e}")
        return f"Failed to get running processes: {str(e)}"

@function_tool()
async def create_file(
    context: RunContext,  # type: ignore
    file_path: str,
    content: str = ""
) -> str:
    """
    Create a new file with optional content.

    Args:
        file_path: Path where to create the file
        content: Optional content to write to the file
    """
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        result = f"Created file: {file_path}"
        if content:
            result += f" with {len(content)} characters"

        logging.info(result)
        return result

    except Exception as e:
        logging.error(f"Error creating file: {e}")
        return f"Failed to create file: {str(e)}"

@function_tool()
async def read_file_content(
    context: RunContext,  # type: ignore
    file_path: str,
    max_chars: int = 1000
) -> str:
    """
    Read content from a file.

    Args:
        file_path: Path to the file to read
        max_chars: Maximum number of characters to read
    """
    try:
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(max_chars)

        if len(content) == max_chars:
            content += f"\n... (truncated, file is larger than {max_chars} chars)"

        result = f"Content of {file_path}:\n{content}"
        logging.info(f"Read file: {file_path}")
        return result

    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return f"Failed to read file: {str(e)}"

@function_tool()
async def delete_file(
    context: RunContext,  # type: ignore
    file_path: str
) -> str:
    """
    Delete a file or directory.

    Args:
        file_path: Path to the file or directory to delete
    """
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            result = f"Deleted file: {file_path}"
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            result = f"Deleted directory: {file_path}"
        else:
            return f"File or directory not found: {file_path}"

        logging.info(result)
        return result

    except Exception as e:
        logging.error(f"Error deleting file: {e}")
        return f"Failed to delete file: {str(e)}"

@function_tool()
async def list_directory(
    context: RunContext,  # type: ignore
    directory_path: str = "."
) -> str:
    """
    List contents of a directory.

    Args:
        directory_path: Path to the directory to list (default: current directory)
    """
    try:
        if not os.path.exists(directory_path):
            return f"Directory not found: {directory_path}"

        items = []
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                items.append(f"📁 {item}/")
            else:
                size = os.path.getsize(item_path)
                items.append(f"📄 {item} ({size} bytes)")

        result = f"Contents of {directory_path}:\n" + "\n".join(items)
        logging.info(f"Listed directory: {directory_path}")
        return result

    except Exception as e:
        logging.error(f"Error listing directory: {e}")
        return f"Failed to list directory: {str(e)}"

@function_tool()
async def get_system_info(
    context: RunContext  # type: ignore
) -> str:
    """
    Get system information including CPU, memory, disk usage.
    """
    try:
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # Memory info
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_total = round(memory.total / (1024**3), 2)  # GB
        memory_used = round(memory.used / (1024**3), 2)   # GB

        # Disk info
        disk = psutil.disk_usage('/')
        disk_percent = round((disk.used / disk.total) * 100, 1)
        disk_total = round(disk.total / (1024**3), 2)     # GB
        disk_used = round(disk.used / (1024**3), 2)       # GB

        result = f"""System Information:
CPU: {cpu_percent}% usage ({cpu_count} cores)
Memory: {memory_percent}% usage ({memory_used}GB / {memory_total}GB)
Disk: {disk_percent}% usage ({disk_used}GB / {disk_total}GB)
Platform: {os.name}"""

        logging.info("System information retrieved")
        return result

    except Exception as e:
        logging.error(f"Error getting system info: {e}")
        return f"Failed to get system information: {str(e)}"

@function_tool()
async def control_volume(
    context: RunContext,  # type: ignore
    action: str,
    level: Optional[int] = None
) -> str:
    """
    Control system volume.

    Args:
        action: 'mute', 'unmute', 'up', 'down', or 'set'
        level: Volume level (0-100) when action is 'set'
    """
    try:
        if action == "mute":
            pyautogui.press('volumemute')
            result = "Volume muted"
        elif action == "unmute":
            pyautogui.press('volumemute')  # Toggle mute
            result = "Volume unmuted"
        elif action == "up":
            pyautogui.press('volumeup')
            result = "Volume increased"
        elif action == "down":
            pyautogui.press('volumedown')
            result = "Volume decreased"
        elif action == "set" and level is not None:
            # Use nircmd for precise volume control on Windows
            subprocess.run(['nircmd.exe', 'setsysvolume', str(int(level * 655.35))],
                         capture_output=True, check=False)
            result = f"Volume set to {level}%"
        else:
            return "Invalid action. Use: mute, unmute, up, down, or set (with level)"

        logging.info(result)
        return result

    except Exception as e:
        logging.error(f"Error controlling volume: {e}")
        return f"Failed to control volume: {str(e)}"

@function_tool()
async def window_management(
    context: RunContext,  # type: ignore
    action: str,
    window_title: Optional[str] = None
) -> str:
    """
    Manage windows (minimize, maximize, close, focus).

    Args:
        action: 'minimize_all', 'show_desktop', 'alt_tab', 'minimize_current', 'maximize_current'
        window_title: Optional window title to focus on specific window
    """
    try:
        if action == "minimize_all":
            pyautogui.hotkey('win', 'm')
            result = "Minimized all windows"
        elif action == "show_desktop":
            pyautogui.hotkey('win', 'd')
            result = "Showing desktop"
        elif action == "alt_tab":
            pyautogui.hotkey('alt', 'tab')
            result = "Switched between windows"
        elif action == "minimize_current":
            pyautogui.hotkey('win', 'down')
            result = "Minimized current window"
        elif action == "maximize_current":
            pyautogui.hotkey('win', 'up')
            result = "Maximized current window"
        else:
            return "Invalid action. Use: minimize_all, show_desktop, alt_tab, minimize_current, maximize_current"

        logging.info(result)
        return result

    except Exception as e:
        logging.error(f"Error managing windows: {e}")
        return f"Failed to manage windows: {str(e)}"

@function_tool()
async def scroll_page(
    context: RunContext,  # type: ignore
    direction: str,
    amount: int = 3
) -> str:
    """
    Scroll the current page or window.

    Args:
        direction: 'up', 'down', 'left', 'right'
        amount: Number of scroll steps
    """
    try:
        for _ in range(amount):
            if direction == "up":
                pyautogui.scroll(1)
            elif direction == "down":
                pyautogui.scroll(-1)
            elif direction == "left":
                pyautogui.hscroll(-1)
            elif direction == "right":
                pyautogui.hscroll(1)
            else:
                return "Invalid direction. Use: up, down, left, right"
            time.sleep(0.1)  # Small delay between scrolls

        result = f"Scrolled {direction} {amount} times"
        logging.info(result)
        return result

    except Exception as e:
        logging.error(f"Error scrolling: {e}")
        return f"Failed to scroll: {str(e)}"

@function_tool()
async def run_command(
    context: RunContext,  # type: ignore
    command: str,
    shell: bool = True
) -> str:
    """
    Run a system command and return the output.

    Args:
        command: Command to execute
        shell: Whether to run in shell mode
    """
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )

        output = f"Command: {command}\n"
        output += f"Return code: {result.returncode}\n"

        if result.stdout:
            output += f"Output:\n{result.stdout}\n"

        if result.stderr:
            output += f"Errors:\n{result.stderr}\n"

        logging.info(f"Executed command: {command}")
        return output

    except subprocess.TimeoutExpired:
        return f"Command timed out: {command}"
    except Exception as e:
        logging.error(f"Error running command: {e}")
        return f"Failed to run command: {str(e)}"

@function_tool()
async def advanced_window_control(
    context: RunContext,  # type: ignore
    action: str,
    window_title: Optional[str] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> str:
    """
    Advanced window control including moving and resizing specific windows.

    Args:
        action: 'find', 'focus', 'move', 'resize', 'close', 'list_windows'
        window_title: Window title to find (partial match)
        x, y: New position for move action
        width, height: New size for resize action
    """
    try:
        import win32gui
        import win32con

        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append((hwnd, title))

        if action == "list_windows":
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            result = "Open windows:\n"
            for hwnd, title in windows[:20]:  # Limit to first 20
                result += f"- {title}\n"
            return result

        if not window_title:
            return "Window title is required for this action"

        # Find window
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)

        target_hwnd = None
        for hwnd, title in windows:
            if window_title.lower() in title.lower():
                target_hwnd = hwnd
                break

        if not target_hwnd:
            return f"Window with title containing '{window_title}' not found"

        if action == "find":
            return f"Found window: {win32gui.GetWindowText(target_hwnd)}"

        elif action == "focus":
            win32gui.SetForegroundWindow(target_hwnd)
            return f"Focused window: {win32gui.GetWindowText(target_hwnd)}"

        elif action == "move" and x is not None and y is not None:
            rect = win32gui.GetWindowRect(target_hwnd)
            current_width = rect[2] - rect[0]
            current_height = rect[3] - rect[1]
            win32gui.SetWindowPos(target_hwnd, 0, x, y, current_width, current_height, 0)
            return f"Moved window to ({x}, {y})"

        elif action == "resize" and width is not None and height is not None:
            rect = win32gui.GetWindowRect(target_hwnd)
            win32gui.SetWindowPos(target_hwnd, 0, rect[0], rect[1], width, height, 0)
            return f"Resized window to {width}x{height}"

        elif action == "close":
            win32gui.PostMessage(target_hwnd, win32con.WM_CLOSE, 0, 0)
            return f"Closed window: {win32gui.GetWindowText(target_hwnd)}"

        else:
            return "Invalid action or missing parameters"

    except Exception as e:
        logging.error(f"Error with window control: {e}")
        return f"Failed to control window: {str(e)}"

@function_tool()
async def mouse_automation(
    context: RunContext,  # type: ignore
    action: str,
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: str = "left",
    duration: float = 0.5
) -> str:
    """
    Advanced mouse automation including drag operations.

    Args:
        action: 'click', 'double_click', 'right_click', 'drag', 'move', 'scroll_up', 'scroll_down'
        x, y: Coordinates for mouse actions
        button: Mouse button ('left', 'right', 'middle')
        duration: Duration for drag operations
    """
    try:
        if action in ['click', 'double_click', 'right_click', 'move', 'drag'] and (x is None or y is None):
            return "Coordinates (x, y) are required for this action"

        if action == "click":
            pyautogui.click(x, y, button=button)
            return f"Clicked at ({x}, {y}) with {button} button"

        elif action == "double_click":
            pyautogui.doubleClick(x, y, button=button)
            return f"Double-clicked at ({x}, {y}) with {button} button"

        elif action == "right_click":
            pyautogui.rightClick(x, y)
            return f"Right-clicked at ({x}, {y})"

        elif action == "move":
            pyautogui.moveTo(x, y, duration=duration)
            return f"Moved mouse to ({x}, {y})"

        elif action == "drag":
            current_pos = pyautogui.position()
            pyautogui.dragTo(x, y, duration=duration, button=button)
            return f"Dragged from ({current_pos.x}, {current_pos.y}) to ({x}, {y})"

        elif action == "scroll_up":
            pyautogui.scroll(3)
            return "Scrolled up"

        elif action == "scroll_down":
            pyautogui.scroll(-3)
            return "Scrolled down"

        else:
            return "Invalid action"

    except Exception as e:
        logging.error(f"Error with mouse automation: {e}")
        return f"Failed mouse automation: {str(e)}"

@function_tool()
async def keyboard_automation(
    context: RunContext,  # type: ignore
    action: str,
    text: Optional[str] = None,
    key: Optional[str] = None,
    modifier: Optional[str] = None
) -> str:
    """
    Advanced keyboard automation with modifier keys.

    Args:
        action: 'type', 'press', 'hotkey', 'hold', 'release'
        text: Text to type
        key: Key to press
        modifier: Modifier key (ctrl, alt, shift, win)
    """
    try:
        if action == "type" and text:
            pyautogui.typewrite(text, interval=0.05)
            return f"Typed: {text}"

        elif action == "press" and key:
            pyautogui.press(key)
            return f"Pressed key: {key}"

        elif action == "hotkey" and key and modifier:
            pyautogui.hotkey(modifier, key)
            return f"Pressed hotkey: {modifier}+{key}"

        elif action == "hold" and key:
            pyautogui.keyDown(key)
            return f"Holding key: {key}"

        elif action == "release" and key:
            pyautogui.keyUp(key)
            return f"Released key: {key}"

        else:
            return "Invalid action or missing parameters"

    except Exception as e:
        logging.error(f"Error with keyboard automation: {e}")
        return f"Failed keyboard automation: {str(e)}"

@function_tool()
async def manage_startup_programs(
    context: RunContext,  # type: ignore
    action: str,
    program_name: Optional[str] = None,
    program_path: Optional[str] = None
) -> str:
    """
    Manage Windows startup programs.

    Args:
        action: 'list', 'add', 'remove'
        program_name: Name of the program for startup
        program_path: Path to the program executable
    """
    try:
        import winreg

        startup_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

        if action == "list":
            startup_programs = []
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_key) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            startup_programs.append(f"{name}: {value}")
                            i += 1
                        except WindowsError:
                            break

                if startup_programs:
                    return "Startup programs:\n" + "\n".join(startup_programs)
                else:
                    return "No startup programs found"
            except Exception as e:
                return f"Error accessing startup programs: {str(e)}"

        elif action == "add" and program_name and program_path:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_key, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, program_name, 0, winreg.REG_SZ, program_path)
                return f"Added {program_name} to startup programs"
            except Exception as e:
                return f"Error adding startup program: {str(e)}"

        elif action == "remove" and program_name:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_key, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, program_name)
                return f"Removed {program_name} from startup programs"
            except Exception as e:
                return f"Error removing startup program: {str(e)}"

        else:
            return "Invalid action or missing parameters"

    except Exception as e:
        logging.error(f"Error managing startup programs: {e}")
        return f"Failed to manage startup programs: {str(e)}"

@function_tool()
async def network_control(
    context: RunContext,  # type: ignore
    action: str,
    interface: Optional[str] = None
) -> str:
    """
    Control network interfaces and get network information.

    Args:
        action: 'list_interfaces', 'disable_wifi', 'enable_wifi', 'get_ip', 'ping'
        interface: Network interface name (for specific actions)
    """
    try:
        if action == "list_interfaces":
            result = subprocess.run(['netsh', 'interface', 'show', 'interface'],
                                  capture_output=True, text=True, shell=True)
            return f"Network interfaces:\n{result.stdout}"

        elif action == "disable_wifi":
            result = subprocess.run(['netsh', 'interface', 'set', 'interface', 'Wi-Fi', 'disabled'],
                                  capture_output=True, text=True, shell=True)
            return "Wi-Fi disabled" if result.returncode == 0 else f"Error: {result.stderr}"

        elif action == "enable_wifi":
            result = subprocess.run(['netsh', 'interface', 'set', 'interface', 'Wi-Fi', 'enabled'],
                                  capture_output=True, text=True, shell=True)
            return "Wi-Fi enabled" if result.returncode == 0 else f"Error: {result.stderr}"

        elif action == "get_ip":
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
            return f"IP Configuration:\n{result.stdout}"

        elif action == "ping" and interface:
            result = subprocess.run(['ping', '-n', '4', interface],
                                  capture_output=True, text=True, shell=True)
            return f"Ping results for {interface}:\n{result.stdout}"

        else:
            return "Invalid action or missing parameters"

    except Exception as e:
        logging.error(f"Error with network control: {e}")
        return f"Failed network control: {str(e)}"

@function_tool()
async def power_management(
    context: RunContext,  # type: ignore
    action: str,
    delay: int = 0
) -> str:
    """
    System power management operations.

    Args:
        action: 'shutdown', 'restart', 'sleep', 'hibernate', 'lock'
        delay: Delay in seconds before executing the action
    """
    try:
        if action == "shutdown":
            cmd = f"shutdown /s /t {delay}"
        elif action == "restart":
            cmd = f"shutdown /r /t {delay}"
        elif action == "sleep":
            cmd = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        elif action == "hibernate":
            cmd = "shutdown /h"
        elif action == "lock":
            cmd = "rundll32.exe user32.dll,LockWorkStation"
        else:
            return "Invalid action. Use: shutdown, restart, sleep, hibernate, lock"

        if delay > 0 and action in ["shutdown", "restart"]:
            result = f"System will {action} in {delay} seconds"
        else:
            result = f"Executing {action}"

        subprocess.run(cmd, shell=True)
        logging.info(f"Power management: {action}")
        return result

    except Exception as e:
        logging.error(f"Error with power management: {e}")
        return f"Failed power management: {str(e)}"

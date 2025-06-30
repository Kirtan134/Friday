# Friday AI Assistant

> _"Just a rather very intelligent system"_ - Your personal AI assistant inspired by Iron Man's FRIDAY

A sophisticated AI assistant built with LiveKit and Google's Realtime API that provides comprehensive device control, memory capabilities, and automation features. Friday can see your screen, control applications, manage files, automate tasks, and remember your preferences - all while maintaining the wit and charm of Tony Stark's AI assistant.

## Features

### Core AI Capabilities

- **Voice Interaction**: Real-time voice conversations using Google's Realtime Model
- **Persistent Memory**: Remembers conversations, preferences, and tasks across sessions
- **Intelligent Responses**: Sarcastic yet helpful responses in the style of Iron Man's FRIDAY
- **Task Management**: Tracks and manages your to-do items and reminders

### Screen & Vision

- **Screenshot Capture**: Full screen or specific region screenshots
- **Visual Analysis**: Find UI elements and images on screen
- **Screen Information**: Get resolution, mouse position, and display details
- **Template Matching**: Locate specific images or UI components

### Input Control & Automation

- **Mouse Control**: Click, drag, move with pixel-perfect precision
- **Keyboard Automation**: Type text, press key combinations, hold/release keys
- **Advanced Input**: Configurable typing speed and click patterns
- **Gesture Support**: Complex mouse movements and gestures

### Application & Window Management

- **Smart App Launching**: Open applications by name with intelligent mapping
- **Window Control**: Move, resize, minimize, maximize, focus windows
- **Process Management**: List, monitor, and terminate running processes
- **Multi-window Support**: Handle multiple instances and complex layouts

### File System Operations

- **File Management**: Create, read, edit, delete files and directories
- **Directory Navigation**: List contents with detailed information
- **Safe Operations**: Proper error handling and permission checks
- **Path Intelligence**: Smart path resolution and validation

### System Control

- **Volume Control**: Mute, unmute, adjust levels, media controls
- **Power Management**: Shutdown, restart, sleep, hibernate with delays
- **Network Control**: Manage Wi-Fi, check connectivity, IP configuration
- **Startup Programs**: Add/remove programs from Windows startup

### External Services

- **Email Integration**: Send emails through Gmail with authentication
- **Web Search**: DuckDuckGo search integration
- **Weather Information**: Real-time weather data for any city
- **API Connectivity**: Extensible for additional services

## Requirements

### Dependencies

All dependencies are listed in `requirements.txt`:

```
livekit-agents
livekit-plugins-google
livekit-plugins-noise-cancellation
pyautogui
opencv-python
psutil
pywin32
pynput
keyboard
mouse
pycaw
requests
python-dotenv
pillow
duckduckgo-search
langchain_community
```

## Installation

### 1. Clone or Download

Download the project files to your desired directory:

```cmd
cd c:\Users\yourusername\
mkdir Friday
cd Friday
```

### 2. Install Python Dependencies

```cmd
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root with your API credentials:

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Google API Configuration
GOOGLE_API_KEY=your_google_api_key

# Gmail Configuration (Optional)
GMAIL_APP_PASSWORD=your_gmail_app_password
GMAIL_USER=your_email@gmail.com
```

### 4. Obtain API Keys

#### LiveKit Setup

1. Sign up at [LiveKit Cloud](https://cloud.livekit.io/)
2. Create a new project
3. Copy your URL, API Key, and API Secret to `.env`

#### Google API Setup

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the "Generative Language API"
4. Create an API key and add to `.env`

#### Gmail Setup (Optional)

1. Enable 2-factor authentication on your Google account
2. Generate an App Password for Gmail
3. Add credentials to `.env`

## Usage

### Starting Friday

```cmd
python agent.py
```

### Basic Commands

Once connected, you can interact with Friday using natural language:

#### Application Control

- _"Open calculator"_
- _"Close notepad"_
- _"Switch to Chrome"_
- _"Minimize all windows"_

#### File Operations

- _"Create a file called notes.txt"_
- _"Read the contents of document.pdf"_
- _"List files in my Downloads folder"_
- _"Delete temp.txt"_

#### Screen Interaction

- _"Take a screenshot"_
- _"Click on the start button"_
- _"Type Hello World"_
- _"Press Ctrl+C"_

#### System Control

- _"Mute the volume"_
- _"Set volume to 50%"_
- _"Shut down the computer in 5 minutes"_
- _"Check my network connection"_

#### Memory & Tasks

- _"Remember that I prefer dark mode"_
- _"What was that website I mentioned yesterday?"_
- _"Add buy groceries to my tasks"_
- _"What are my current tasks?"_

#### Information & Services

- _"What's the weather in New York?"_
- _"Search for Python tutorials"_
- _"Send an email to john@example.com"_
- _"What's my CPU usage?"_

### Advanced Features

#### Memory System

Friday automatically remembers:

- Your conversations and interactions
- Personal preferences and settings
- Tasks and reminders
- Important information you share

Access memory with commands like:

- _"Remember my favorite coffee is espresso"_
- _"What did I say about the project deadline?"_
- _"Show me my completed tasks"_

#### Automation Scripts

You can chain commands for complex automation:

- _"Open notepad, type my daily schedule, and save it as today.txt"_
- _"Take a screenshot, then email it to my manager"_
- _"Set volume to 30%, open Spotify, and play my focus playlist"_

## Project Structure

```
Friday/
├── agent.py              # Main AI agent with LiveKit integration
├── tools.py              # All function tools and capabilities
├── prompts.py            # AI personality and instructions
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── friday_memory.json    # Memory storage (auto-created)
├── test_capabilities.py  # Testing script
└── README.md            # This documentation
```

### Core Files

- **`agent.py`**: Main entry point that sets up the LiveKit agent, registers tools, and handles the conversation flow
- **`tools.py`**: Contains all function tools for device control, file operations, system management, and memory
- **`prompts.py`**: Defines Friday's personality, instructions, and response patterns
- **`friday_memory.json`**: Automatically created file that stores conversations, preferences, and tasks

## Configuration

### Customizing Friday's Personality

Edit `prompts.py` to modify:

- Response style and tone
- Available capabilities descriptions
- Example interactions
- Behavioral guidelines

### Adding New Tools

To add new capabilities:

1. Define a new function in `tools.py` with the `@function_tool()` decorator
2. Add the function to the tools list in `agent.py`
3. Update the documentation in `prompts.py`

### Memory Configuration

Memory settings can be modified in `tools.py`:

- Conversation history limit (default: 50 entries)
- Memory file location
- Data retention policies


## Security Considerations

### API Keys

- Never commit `.env` file to version control
- Use environment variables in production
- Regularly rotate API keys
- Limit API key permissions where possible

### System Access

- Friday has extensive system access - use responsibly
- Review tool permissions before deployment
- Consider running in restricted environment for testing
- Monitor automated actions for unexpected behavior

### Data Privacy

- Memory data is stored locally in JSON format
- No conversation data is sent to external services except LiveKit
- Email credentials are only used for sending emails
- Consider encrypting memory file for sensitive data

##  Advanced Usage

### Custom Integrations

Extend Friday with additional services:

```python
@function_tool()
async def custom_integration(context: RunContext, parameter: str) -> str:
    """Your custom tool description"""
    # Implementation here
    return "Success message"
```

### Automation Scripts

Create complex workflows:

```python
# Example: Morning routine automation
async def morning_routine():
    await open_application(None, "outlook")
    await control_volume(None, "set", 40)
    await capture_screen(None, "morning_desktop.png")
    await send_email(None, "boss@company.com", "Daily Check-in", "Good morning! Ready for the day.")
```

### Integration with Other Systems

- Connect to home automation systems
- Integrate with project management tools
- Add support for additional cloud services
- Create custom reporting and analytics

## 📝 Contributing

### Adding New Features

1. Fork the repository or create a feature branch
2. Add new tools following the existing pattern
3. Update documentation and prompts
4. Test thoroughly on Windows systems
5. Submit pull request with clear description

### Testing

- Test all new features on Windows 10/11
- Verify LiveKit integration works
- Ensure no breaking changes to existing tools
- Add test cases for new functionality

## 📄 License

This project is provided as-is for educational and personal use. Please respect the terms of service for all integrated APIs and services.


### Community

- Share improvements and customizations
- Report bugs and suggest features
- Help others with troubleshooting
- Contribute to documentation

---

_"Sometimes you gotta run before you can walk."_ - Tony Stark

Enjoy your new AI assistant! Friday is ready to help you automate, control, and enhance your computing experience with the wit and intelligence worthy of the Stark name.

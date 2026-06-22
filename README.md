# qBittorrent Auto-Ban Leecher

A lightweight Python script that automatically detects and globally bans "leeching" clients (such as Xunlei, BitComet, etc.) from your qBittorrent instance.

## Features
* **Global IP Banning**: Directly modifies qBittorrent's global `banned_IPs` list for persistent protection.
* **Customizable Patterns**: Easily add new client signatures to the `LEECH_PATTERNS` list.
* **Graceful Operation**: Designed to run in the background with configurable refresh intervals.
* **Case-Insensitive Matching**: Effectively detects clients regardless of string casing.

## Setup

### 1. Requirements
This script uses standard Python libraries. No external dependencies (like pip) are required.

### 2. Configuration
Open the `ban_xunlei.py` file and configure the variables at the top to match your environment:

```python
# --- User Configuration ---
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 'WebUI_Port'
USERNAME = 'your_username'
PASSWORD = 'your_password'

# Add client signatures you wish to ban
LEECH_PATTERNS = ['XunLei', '-XL', 'Thunder', 'BitComet']
# --------------------------
```

### 3. Usage
Run the script directly via terminal:

```bash
python ban_xunlei.py
```

### Security Warning
Important: If you plan to make this repository public, please remove or obfuscate your username and password from the script before pushing to GitHub. Consider using environment variables or a separate config file to store sensitive credentials.

### License
This project is open-source and available for personal use.

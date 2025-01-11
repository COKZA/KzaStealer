import sys
import os
import shutil
from pathlib import Path

def add_to_startup(script_path=None):
    # إذا لم يتم تحديد مسار السكربت، يتم استخدام ملف البرنامج الحالي
    if script_path is None:
        script_path = sys.argv[0]

    # تحديد مسار Startup (ملف البرامج التي تعمل عند بدء التشغيل)
    startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

    # التحقق من وجود المجلد
    if not startup_folder.exists():
        return

    # نسخ ملف السكربت إلى مجلد Startup
    script_name = Path(script_path).name
    destination = startup_folder / script_name

    try:
        shutil.copy(script_path, destination)
    except Exception as e:
        print(f"Error copying file: {e}")

# استدعاء الوظيفة
add_to_startup()

import configparser
from pathlib import Path
import subprocess

# 📁 Dynamic base directory
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.ini"

# 📖 Load config
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# 🗓 Prompt for Thai Buddhist dates
print("📅 Enter date range (Thai calendar, e.g. 1/10/2568)")
start_date = input("Start date: ").strip()
end_date = input("End date: ").strip()

# 📝 Update config
config["dates"]["start_date"] = start_date
config["dates"]["end_date"] = end_date

with open(CONFIG_PATH, "w") as configfile:
    config.write(configfile)

print("✅ Config updated.")

# 🚀 Choose script to run
print("\nWhich script would you like to run?")
print("1. Run E-stamp Downloader")
print("2. Run Receipt Downloader")
print("3. Run Merge")

choice = input("Enter 1, 2, or 3: ").strip()

try:
    if choice == "1":
        subprocess.run(["python", str(BASE_DIR / "download_estamp_v1.05.py")])
    elif choice == "2":
        subprocess.run(["python", str(BASE_DIR / "download_receipt_v1.05.py")])
    elif choice == "3":
        subprocess.run(["python", str(BASE_DIR / "merge_files_v1.02.py")])
    else:
        print("❌ Invalid choice.")
except Exception as e:
    print(f"❌ Failed to run script: {e}")
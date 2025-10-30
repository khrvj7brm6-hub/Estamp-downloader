import re
import configparser
from pathlib import Path
from PyPDF2 import PdfMerger

# 📁 Dynamic base directory (works in .exe too)
BASE_DIR = Path(__file__).resolve().parent

# 📖 Load config
config_path = BASE_DIR / "config.ini"
config = configparser.ConfigParser()
config.read(config_path)

# 📂 Resolve folders relative to BASE_DIR
estamp_dir = BASE_DIR / config["folders"]["estamp_dir"]
receipt_dir = BASE_DIR / config["folders"]["receipt_dir"]
merged_dir = BASE_DIR / config["folders"]["merged_dir"]
merged_dir.mkdir(parents=True, exist_ok=True)

cleanup_enabled = config.getboolean("settings", "cleanup_after_merge", fallback=False)

def extract_id_and_date(filename):
    match = re.search(r"P\d{11,13}_(\d{8})", filename)
    id_match = re.search(r"P\d{11,13}", filename)
    date_match = match.group(1) if match else None
    return (id_match.group(0) if id_match else None, date_match)

# 📌 Index e-stamp files by ID
estamp_index = {}
for f in estamp_dir.glob("*.pdf"):
    pid, date = extract_id_and_date(f.name)
    if pid and date:
        estamp_index[pid] = (f, date)

# 📌 Index receipt files by ID
receipt_index = {}
for f in receipt_dir.glob("*.pdf"):
    pid = extract_id_and_date(f.name)[0]
    if pid:
        receipt_index[pid] = f

# 🔗 Merge matching pairs
for pid, (estamp_path, date) in estamp_index.items():
    if pid in receipt_index:
        receipt_path = receipt_index[pid]
        merger = PdfMerger()
        merger.append(estamp_path)
        merger.append(receipt_path)
        output_path = merged_dir / f"{date}_{pid}.pdf"
        merger.write(output_path)
        merger.close()
        print(f"✅ Merged: {output_path}")
    else:
        print(f"⚠️ No matching receipt for {pid}")

# 🧹 Optional cleanup
if cleanup_enabled:
    print("🧹 Cleanup enabled. Removing unmerged PDFs...")
    for f in estamp_dir.glob("*.pdf"):
        f.unlink()
    for f in receipt_dir.glob("*.pdf"):
        f.unlink()
    print("✅ Cleanup completed.")
else:
    print("🚫 Cleanup skipped based on config flag.")
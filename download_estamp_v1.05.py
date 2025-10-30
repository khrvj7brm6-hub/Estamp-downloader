import asyncio
import base64
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import configparser

# Base directory (dynamic, works in .exe too)
BASE_DIR = Path(__file__).resolve().parent

# Load config
config_path = BASE_DIR / "config.ini"
config = configparser.ConfigParser()
config.read(config_path)

headless_mode = config.getboolean("settings", "headless", fallback=True)
halt_on_skip = config.getboolean("settings", "halt_on_skip", fallback=False)

def is_date_in_range(date_str, start_date, end_date):
    try:
        day, month, year = map(int, date_str.split("/"))
        gregorian_year = year - 543
        date_obj = datetime(gregorian_year, month, day)
        return start_date <= date_obj <= end_date
    except:
        return False

def parse_thai_date(date_str):
    day, month, year = map(int, date_str.split("/"))
    gregorian_year = year - 543
    return datetime(gregorian_year, month, day)

async def download_receipts():
    rd_id = config["credentials"]["rd_id"].strip('"')
    rd_password = config["credentials"]["rd_password"].strip('"')

    start_date = parse_thai_date(config["dates"]["start_date"])
    end_date = parse_thai_date(config["dates"]["end_date"])

    save_dir = BASE_DIR / config["folders"]["estamp_dir"]
    save_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless_mode)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://efiling.rd.go.th/rd-efiling-web/authen/OS9_V2")

        # Auto-fill login form
        await page.fill('input[formcontrolname="username"]', rd_id)
        await page.fill('input[formcontrolname="password"]', rd_password)
        await page.click('button.btn-login')
        await page.wait_for_timeout(5000)

        await page.goto("https://efiling.rd.go.th/rd-stamp-os9-web/#/receipt")
        await page.wait_for_timeout(5000)

        # Extract total number of pages
        total_pages = await page.evaluate("""
            () => {
                const items = Array.from(document.querySelectorAll('li.ant-pagination-item'));
                const pageNumbers = items.map(li => parseInt(li.textContent.trim())).filter(n => !isNaN(n));
                return Math.max(...pageNumbers);
            }
        """)
        print(f"Total pages detected: {total_pages}")

        for page_num in range(1, total_pages + 1):
            print(f"\nProcessing page {page_num} of {total_pages}")
            if page_num > 1:
                page_btn = await page.query_selector(f"li.ant-pagination-item[title='{page_num}']")
                if page_btn:
                    await page_btn.click()
                    await page.wait_for_timeout(3000)

            icons = await page.query_selector_all("i.fas.fa-file-pdf.fa-stack-1x.fa-inverse")
            print(f"Found {len(icons)} icons on page {page_num}")

            for i, icon in enumerate(icons):
                script_info = await page.evaluate("""(el) => {
                    const row = el.closest('tr');
                    if (!row) return null;
                    const cells = Array.from(row.querySelectorAll('td'));
                    let id = null, date = null;
                    for (const td of cells) {
                        const text = td.textContent.trim();
                        if (/^P\\d{11,13}$/.test(text)) id = text;
                        if (/\\d{2}\\/\\d{2}\\/\\d{4}/.test(text)) date = text;
                    }
                    return id && date ? { id, date } : null;
                }""", icon)

                if not script_info or not is_date_in_range(script_info['date'], start_date, end_date):
                    print(f" Skipping document {i+1} on page {page_num} — date not in range.")
                    if halt_on_skip:
                        print(" Config flag 'halt_on_skip' is enabled. Stopping execution.")
                        await browser.close()
                        sys.exit(1)
                    else:
                        continue

                async with page.expect_popup() as popup_info:
                    await icon.click()
                viewer_page = await popup_info.value
                await viewer_page.wait_for_load_state()
                await viewer_page.wait_for_timeout(3000)

                try:
                    pdf_data_url = await viewer_page.evaluate("""
                        () => {
                            const embed = document.querySelector('embed[type="application/pdf"]');
                            if (embed && embed.src.startsWith('data:application/pdf;base64,')) return embed.src;

                            const object = document.querySelector('object[type="application/pdf"]');
                            if (object && object.data.startsWith('data:application/pdf;base64,')) return object.data;

                            return null;
                        }
                    """)

                    if pdf_data_url:
                        base64_data = pdf_data_url.split(',')[1]
                        pdf_bytes = base64.b64decode(base64_data)

                        formatted_date = script_info['date'].replace("/", "")
                        filename = save_dir / f"e-stampduty_{script_info['id']}_{formatted_date}.pdf"

                        with open(filename, "wb") as f:
                            f.write(pdf_bytes)

                        print(f" Saved {filename}")
                    else:
                        print(f"⚠No base64 PDF stream found for document {i+1} on page {page_num}")

                except Exception as e:
                    print(f" Failed to process document {i+1} on page {page_num}: {e}")

                await viewer_page.close()

        await browser.close()

asyncio.run(download_receipts())
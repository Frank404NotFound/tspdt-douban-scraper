import requests
from bs4 import BeautifulSoup
import re
import time
import csv
import os
import random

def extract_and_save_ids_with_titles(doulist_url, filename="COOKIEtspdt1000doubanID.csv", summary_file="tspdt1000_summary.txt"):
    headers = {
#TO BE REPLACED
    }


    # Init CSV if needed
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["douban_film_id", "title", "page_number", "rank_within_list"])

    page = 0
    all_count = 0
    pages_with_issues = []

    while True:
        url = f"{doulist_url}?start={page * 25}&sort=seq&sub_type="
        print(f"Fetching page {page+1}: {url}")

        # Retry logic
        for attempt in range(3):
            try:
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    break
                else:
                    print(f"HTTP error {res.status_code}, retrying...")
            except Exception as e:
                print(f"Request error: {e}, retrying...")

            wait_time = 2 ** attempt + random.uniform(0.5, 1.5)
            time.sleep(wait_time)
        else:
            print(f"Failed to fetch page {page+1} after 3 attempts.")
            break

        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("div.doulist-item div.title a[href*='movie.douban.com/subject/']")

        seen = set()
        film_data = []

        for idx, a in enumerate(items):
            href = a.get("href")
            match = re.search(r'/subject/(\d+)/', href)
            if match:
                film_id = match.group(1)
                title = a.get_text(strip=True)
                if film_id not in seen:
                    seen.add(film_id)
                    rank = page * 25 + len(film_data) + 1
                    film_data.append((film_id, title, page + 1, rank))

        # Warn if missing items
        if len(film_data) < 25:
            print(f"⚠️ Page {page+1} has only {len(film_data)} items!")
            pages_with_issues.append((page + 1, len(film_data)))

        if not film_data:
            print("No new entries found. Ending.")
            break

        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in film_data:
                writer.writerow(row)

        all_count += len(film_data)
        print(f"✅ Page {page+1}: {len(film_data)} entries written. Total so far: {all_count}")
        page += 1
        time.sleep(random.uniform(1.5, 3.0))

    # Save summary log
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"✔ Scraped {all_count} films across {page} pages.\n")
        if pages_with_issues:
            f.write("\n⚠ Pages with fewer than 25 items:\n")
            for p, count in pages_with_issues:
                f.write(f"  - Page {p}: {count} items\n")
        else:
            f.write("\nAll pages returned 25 items.\n")
        f.write(f"\nSource: {doulist_url}\n")

    print(f"\n📄 Summary written to {summary_file}")

# Example
doulist_url = "https://www.douban.com/doulist/134519598/"
extract_and_save_ids_with_titles(doulist_url)

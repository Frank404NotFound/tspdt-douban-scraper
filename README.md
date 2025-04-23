# TSPDT x Douban Scraper

A lightweight Python project that extracts Douban film data for titles in the **TSPDT All-Time 1000** list, focusing on **friend-based ratings** and **vote counts**. Designed to explore how global critical consensus aligns (or diverges) from social viewing habits on Douban.

---

## 🎯 MVP Goal

- Take the canonical **TSPDT 1000** list
- Map each film to its **Douban ID**
- Extract:
  - **Friend rating**
  - **Overall rating**
  - **Rating count**
- Save results to CSV for further sorting, filtering, and analysis

---

## 🛠️ Current Features

- ✅ Scrapes film ID and title from Douban Doulists
- ✅ Supports full list pagination
- ✅ Handles login-only entries (via cookie injection)
- ✅ Outputs structured CSV
- ✅ Logs incomplete pages for review

---

## 🚧 In Progress / Future Ideas

- Map to **IMDb**, **Letterboxd**, and **TSPDT 21st Century**
- Normalize film titles across platforms
- Visualize rating gaps between Douban friends and TSPDT rank
- Surface overlooked or socially popular outliers

---

## 🧰 Requirements

- `requests`
- `beautifulsoup4`
- Your own **Douban cookie** (to access all list items)

---

## ✏️ Usage

1. Paste your Doulist URL (e.g. for TSPDT 1000)
2. Run the script
3. Get a CSV with film IDs, titles, and ranks
4. Use the CSV to query Douban for rating data

---

## 📎 Disclaimer

This is an exploratory, personal project for cinephile research and metadata analysis. Not affiliated with Douban or TSPDT.

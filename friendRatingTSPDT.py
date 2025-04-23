import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

# Load Douban ID CSV
INPUT_CSV = "tspdt1000doubanID.csv"
OUTPUT_CSV = "tspdt1000_with_friends_sample.csv"
SAVE_INTERVAL = 5  # Save the file every 5 entries
HEADERS = {

}

def extract_douban_fields(douban_id, max_retries=3):
    url = f"https://movie.douban.com/subject/{douban_id}/"
    for attempt in range(max_retries):
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code != 200:
                print(f"Failed to fetch {url} - Status code: {res.status_code}")
                return (None, None, None, None, None)

            soup = BeautifulSoup(res.text, "html.parser")

            douban_rating = soup.select_one('strong.rating_num')
            douban_rating = float(douban_rating.text.strip()) if douban_rating else None

            vote_span = soup.select_one('span[property="v:votes"]')
            douban_votes = int(vote_span.text.strip()) if vote_span else None

            friend_rating = soup.select_one('.friends_rating_wrap strong.rating_avg')
            friend_rating = float(friend_rating.text.strip()) if friend_rating else None

            friend_count_tag = soup.select_one('.friends_rating_wrap a.friends_count')
            if friend_count_tag:
                match = re.search(r'(\d+)', friend_count_tag.text)
                friend_count = int(match.group(1)) if match else 0
            else:
                friend_count = 0

            imdb_id = None
            for span in soup.select('#info span.pl'):
                if 'IMDb' in span.text:
                    next_sibling = span.next_sibling
                    if isinstance(next_sibling, str):
                        match = re.search(r'tt\d+', next_sibling)
                        if match:
                            imdb_id = match.group(0)
                            break

            return douban_rating, douban_votes, friend_rating, friend_count, imdb_id

        except Exception as e:
            print(f"Error scraping {douban_id} (attempt {attempt+1}/{max_retries}): {e}")
            time.sleep(2 * (attempt + 1))  # Exponential backoff

    return (None, None, None, None, None)

def save_progress(df, filename, current_idx):
    """Save the current progress to a file"""
    df.to_csv(filename, index=False)
    print(f"💾 Progress saved at entry {current_idx+1}/{len(df)} to {filename}")

def main():
    # Read the entire file first
    full_df = pd.read_csv(INPUT_CSV)
    
    # You can choose to scrape just a subset if needed
    # df = full_df.head(10)  # only scrape first 10 entries
    df = full_df  # scrape all entries
    
    # Check if there's an existing output file to resume from
    try:
        existing_df = pd.read_csv(OUTPUT_CSV)
        # Identify which entries have already been processed
        processed_ids = set(existing_df['douban_film_id'])
        
        # Filter out already processed entries
        df = df[~df['douban_film_id'].isin(processed_ids)]
        
        # Use the existing data
        result_df = existing_df
        print(f"Found existing file with {len(existing_df)} entries. {len(df)} entries left to process.")
    except FileNotFoundError:
        # Start fresh
        result_df = pd.DataFrame(columns=df.columns.tolist() + 
                               ['douban_rating', 'douban_votes', 'friend_rating', 'friend_rating_count', 'imdb_id'])
        print(f"Starting fresh with {len(df)} entries to process.")
    
    for idx, row in df.iterrows():
        douban_id = row['douban_film_id']
        print(f"Scraping {douban_id} ({idx+1}/{len(df)})...")
        
        douban_rating, douban_votes, friend_rating, friend_count, imdb_id = extract_douban_fields(douban_id)
        
        # Create a new row with all data
        new_row = row.to_dict()
        new_row.update({
            'douban_rating': douban_rating,
            'douban_votes': douban_votes,
            'friend_rating': friend_rating,
            'friend_rating_count': friend_count,
            'imdb_id': imdb_id
        })
        
        # Append the new row to the result dataframe
        result_df = pd.concat([result_df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Save periodically
        if (idx + 1) % SAVE_INTERVAL == 0 or idx == len(df) - 1:
            save_progress(result_df, OUTPUT_CSV, idx)
        
        time.sleep(1.5)  # polite delay

    print(f"✅ Done. All data saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
# scrapper.py
import json
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")   # headless for GitHub runner
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Do NOT pass a driver_path here – Selenium will download/locate it
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# URL to scrape
url = "https://music.amazon.com/popular/songs"

def scrape_top_100():
    # Start browser
    driver = get_driver()
    driver.get(url)
    time.sleep(5)

    song_title = []
    artist_name = []
    image_url = []
    target_count = 100

    while len(song_title) < target_count:
        # Get current page HTML
        webpage = driver.page_source
        soup = BeautifulSoup(webpage, 'lxml')

        trending_songs = soup.find_all('music-horizontal-item')

        for song in trending_songs:
            # Safely extract attributes
            primary_text = song.get('primary-text', '0. Unknown Title')
            # Some items may not include a dot, so guard split
            if "." in primary_text:
                title = primary_text.split(".", 1)[1].strip()
            else:
                title = primary_text.strip()

            artist = song.get('secondary-text', 'Unknown Artist')
            img = song.get('image-src', 'Image Not Found')

            song_title.append(title)
            artist_name.append(artist)
            image_url.append(img)

        print(f"Collected {len(song_title)} songs...")

        if len(song_title) >= target_count:
            break

        # Scroll to load more items
        driver.execute_script("window.scrollBy(0, 2000);")
        time.sleep(2)

    driver.quit()

    # Create DataFrame with the first 100 songs
    songs_data = pd.DataFrame({
        "Track": song_title[:target_count],
        "Artists": artist_name[:target_count],
        "Image Url": image_url[:target_count]
    })

    return songs_data

def main():
    songs_data = scrape_top_100()
    print("Final count:", len(songs_data))

    # Convert DataFrame to list of dicts and save as JSON in same folder
    records = songs_data.to_dict(orient="records")  # one dict per row [web:14][web:18][web:19]

    # Write to data.json in same folder as scrapper.py
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)  # [web:11][web:14]

    print("Saved data to data.json")

if __name__ == "__main__":
    main()

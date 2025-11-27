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
    driver = get_driver()
    print("Opening page...")
    driver.get(url)
    time.sleep(5)
    print("Page loaded")

    song_title = []
    artist_name = []
    image_url = []
    target_count = 100

    start_time = time.time()
    MAX_SECONDS = 240  # stop after 4 minutes max

    while len(song_title) < target_count:
        # safety timeout
        if time.time() - start_time > MAX_SECONDS:
            print("Stopping: hit max runtime limit")
            break

        print(f"Loop start, currently have {len(song_title)} songs")

        webpage = driver.page_source
        soup = BeautifulSoup(webpage, 'html.parser')

        trending_songs = soup.find_all('music-horizontal-item')
        print(f"Found {len(trending_songs)} items on this view")

        for song in trending_songs:
            primary_text = song.get('primary-text', '0. Unknown Title')
            if "." in primary_text:
                title = primary_text.split(".", 1)[1].strip()
            else:
                title = primary_text.strip()

            artist = song.get('secondary-text', 'Unknown Artist')
            img = song.get('image-src', 'Image Not Found')

            song_title.append(title)
            artist_name.append(artist)
            image_url.append(img)

            if len(song_title) >= target_count:
                break

        print(f"Collected {len(song_title)} songs so far")

        if len(song_title) >= target_count:
            break

        driver.execute_script("window.scrollBy(0, 2000);")
        time.sleep(2)

    driver.quit()
    print("Driver closed")

    songs_data = pd.DataFrame({
        "Track": song_title[:target_count],
        "Artists": artist_name[:target_count],
        "Image Url": image_url[:target_count]
    })

    return songs_data


def main():
    print("Scraper main() started")
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

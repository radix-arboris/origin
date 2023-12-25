'''
docker build -t origin-news .
docker run --name originnews origin-news
docker stop originnews
docker rm originnews
docker rmi origin-news

'''

# RSS Feed URLS start with the https:// otherwise everything is just the subdomain and/or subdirectory
urls = [
    # biz urls
    [
        'finance.yahoo.com',
        'www.foxbusiness.com',
        'www.bloomberg.com',
        'www.cnbc.com',
        'www.marketwatch.com',
        'www.wsj.com',
        'www.ft.com',
        'www.economist.com',
        'www.businessinsider.com',
        'www.barrons.com',
    ],

    # politics urls

    [
        'www.theatlantic.com',
        'therecord.media',
        'www.wired.com',
        'www.zdnet.com',
        'medium.com',
        'www.theepochtimes.com',
        'www.dailywire.com',
        'www.yahoo.com',
        'www.nytimes.com',
        'www.washingtonpost.com',
        'www.foxnews.com',
        'www.politico.eu',
        'https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best',
        'www.cnbc.com',
        'www.cnn.com',
        'www.msnbc.com'
    ],

    # gov urls
    [
        'www.whitehouse.gov/briefing-room/statements-releases',
        'www.govtrack.us/congress/bills',
        'www.senate.gov/legislative/bills_acts_laws.htm',
        'www.commerce.gov/news/press-releases',
        'www.justice.gov/blogs',
    ],
] 

import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
from transformers import pipeline, BertForTokenClassification, BertTokenizer
from tqdm import tqdm
from datetime import datetime
from time import sleep
import logging
import feedparser

# Suppress TensorFlow INFO and WARNING messages
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# Initialize the headline counter
headline_counter = 0
log_file_path = './headlines.log'

# Define user agent headers
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def extract_headlines(html_content, domain):
    global headline_counter  # Use the global headline counter

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all heading elements (h1 to h6)
    heading_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'yt-formatted-string'])
    headlines_from_headings = [element.text.strip() for element in heading_elements if element.text.strip()]

    # Combine the headlines from all sources
    all_headlines = headlines_from_headings

    # Filter out headlines shorter than min_words words because they are probably not headlines
    min_words = 4
    filtered_headlines = [headline for headline in all_headlines if len(headline.split()) >= min_words]

    # Log the headlines to the file
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        for headline in filtered_headlines:
            headline_counter += 1  # Increment the headline counter

            # format headlines for log entry
            headline = headline.replace("’", "'")
            headline = headline.replace("‘", "'")
            headline = headline.replace("\"", "'")

            # Construct the Yandex search link for the headline
            encoded_headline = urllib.parse.quote(headline)
            article_link = f"https://yandex.com/search/?text={encoded_headline.replace('%20', '+')}"

            log_entry = f"{datetime.now().strftime('%m%d%H%M%S')}   {domain}   {headline_counter}   \"{headline}\"   \"{article_link}\""
            log_file.write(log_entry + '\n')

    return filtered_headlines

def extract_headlines_from_rss(feed_url):
    global headline_counter  # Use the global headline counter

    # Parse the RSS feed
    feed = feedparser.parse(feed_url)

    # Extract headlines from the RSS feed
    headlines = [entry.title for entry in feed.entries]

    # Log the headlines to the file
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        for headline in headlines:
            headline_counter += 1  # Increment the headline counter

            # format headlines for log entry
            headline = headline.replace("’", "'")
            headline = headline.replace("‘", "'")
            headline = headline.replace("\"", "'")

            # Construct the Yandex search link for the headline
            encoded_headline = urllib.parse.quote(headline)
            article_link = f"https://yandex.com/search/?text={encoded_headline.replace('%20', '+')}"

            log_entry = f"{datetime.now().strftime('%m%d%H%M%S')}   {feed_url}   {headline_counter}   \"{headline}\"   \"{article_link}\""
            log_file.write(log_entry + '\n')

    return headlines

def fetch_html_content(url):
    # Ensure the .html_cache directory exists
    html_cache_dir = './.html_cache'
    os.makedirs(html_cache_dir, exist_ok=True)

    # Extract the domain name from the URL
    domain_name = urllib.parse.urlparse(url).hostname

    # Set the file path to store the downloaded HTML content
    html_cache_file = os.path.join(html_cache_dir, f"{domain_name}_downloaded_html.html")

    if os.path.isfile(html_cache_file):
        # If the HTML content is already downloaded, read it from the file
        print("Using cached HTML content.")
        with open(html_cache_file, 'rb') as file:
            return file.read()
    else:
        # Download HTML content from the URL
        print(f"\nDownloading HTML content from {url}")
        response = requests.get(url, headers=headers)  # Use user agent headers
        if response.status_code == 200:
            print("HTML content downloaded successfully.")
            # Save the HTML content to the cache file
            with open(html_cache_file, 'wb') as file:
                file.write(response.content)
            return response.content
        else:
            print(f"Failed to retrieve HTML content from {url}. Status code: {response.status_code}")
            return None

def download_ner_model():
    # Ensure the .model directory exists
    model_dir = './.model'
    os.makedirs(model_dir, exist_ok=True)

    # Check if the model is already present in the specified directory
    if os.path.exists(os.path.join(model_dir, "dbmdz/bert-large-cased-finetuned-conll03-english")):
        # Load the model from the local directory
        model = BertForTokenClassification.from_pretrained(model_dir)
        tokenizer = BertTokenizer.from_pretrained(model_dir)
        nlp = pipeline("ner", model=model, tokenizer=tokenizer, device=0)
        print("NER model loaded from cache.")
    else:
        # If the model is not present, download it to the local directory
        print("Downloading NER model...")
        nlp = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", device=0)
        print("NER model downloaded successfully.")

    return nlp

def main():
    global headline_counter  # Use the global headline counter

    # Check if the NER model is already downloaded
    model_dir = './.model'
    nlp = None

    if os.path.exists(model_dir) and os.listdir(model_dir):
        print("NER model is already downloaded.")
        nlp = pipeline("ner", model=model_dir, device=0)
    else:
        # Download the NER model
        nlp = download_ner_model()

    # Open the log file in append mode
    log_file_path = './headlines.log'
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        # Iterate over each category of URLs (including RSS feeds)
        for category_urls in urls:
            for url in category_urls:
                if url.startswith('https://'):
                    # If the URL is an RSS feed, extract headlines directly
                    headlines = extract_headlines_from_rss(url)
                else:
                    # add back the beginning of he url
                    url = 'https://' + url

                    # Fetch HTML content from the URL
                    html_content = fetch_html_content(url)

                    if html_content:
                        if nlp:
                            # Extract headlines using the NLP model
                            headlines = extract_headlines(html_content, urllib.parse.urlparse(url).hostname)
                            # Introduce a delay between requests
                            #sleep(2)
                        else:
                            print("Failed to load NER model.")
                    else:
                        print("Skipping News Source.")

if __name__ == "__main__":
    main()

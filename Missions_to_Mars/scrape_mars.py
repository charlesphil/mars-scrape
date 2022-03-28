# Import dependencies
import time
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import requests
from selenium.common.exceptions import WebDriverException
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


def scrape():
    # Set up a windowless Splinter browser with Chrome webdriver to use later 
    # when interacting with the NASA News and Mars Facts pages
    # Try with Chrome first
    try:
        executable_path = {"executable_path": ChromeDriverManager().install()}
        browser = Browser("chrome", **executable_path, headless=True)
    # If Chrome is not installed, try with Firefox
    except WebDriverException:
        executable_path = {"executable_path": GeckoDriverManager().install()}
        browser = Browser("firefox", **executable_path, headless=True)

    # Splinter browser
    url = ("https://mars.nasa.gov/news/?page=0&per_page=40"
           + "&order=publish_date+desc%2Ccreated_at+desc&search="
           + "&category=19%2C165%2C184%2C204&blank_scope=Latest")
    browser.visit(url)

    # NASA loads certain elements using JS, and can cause problems if we load 
    # the HTML too quickly. Sleep for one second to let their JS do its thing.
    time.sleep(1)

    # Grab HTML from Splinter browser visit
    html = browser.html
    soup = BeautifulSoup(html, "lxml")

    # Select the most recent article (select_one method returns first instance)
    latest_article = soup.select_one("li.slide")

    # Grab article's title, paragraph, and url
    latest_title = latest_article.select_one("div.content_title").text
    latest_para = latest_article.select_one("div.article_teaser_body").text
    latest_url = f"https://mars.nasa.gov{latest_article.a['href']}"

    # Grab article's full-res image from article link
    browser.visit(latest_url)
    html = browser.html
    soup = BeautifulSoup(html, "lxml")
    latest_img = f"https://mars.nasa.gov{soup.select_one('#main_image')['src']}"

    # Save in a dictionary for quick access
    latest_news = {
        "title": latest_title,
        "paragraph": latest_para,
        "img": latest_img,
        "url": latest_url
    }

    # Scrape with requests module serving the HTML
    url = "https://mars.nasa.gov/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    # Select the image of the week's src attribute and the name of the image

    # NASA uses js imageScroll to convert img tag
    featured_image = soup.select_one("#featured_image")
    featured_url = f"https://mars.nasa.gov{featured_image['data-image']}"

    # Select the Image of the Week's Name
    featured_name = soup.select_one(".image_of_the_day"). \
        select_one(".media_feature_title").text.strip()

    # Get link to the article page for the image of the week
    article_url = soup.select_one(".header_link")["href"]

    # Store name, image url, and article url of featured image
    image_of_week = {
        "name": featured_name,
        "img_url": featured_url,
        "article_url": article_url
    }

    # Read any available tables from the web page (should be just one)
    url = "https://mars.nasa.gov/all-about-mars/facts/"
    facts_table = pd.read_html(url)
    df = facts_table[0]

    # Table looks remarkably clean, just get rid of the name of the first column
    df = df.rename(columns={"Unnamed: 0": ""})

    # Convert to HTML table
    html_facts_table = df.to_html(
        index=False,
        classes=[
            "table",
            "table-bordered",
            "table-striped",
            "table-dark",
            "m-0"
        ],
        justify="center"
    )

    # Need to interact with website for img, use Splinter
    url = ("https://astrogeology.usgs.gov/search/results?"
           + "q=hemisphere+enhanced&k1=target&v1=Mars")
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, "lxml")

    # Get all hemispheres from the results page
    hemispheres = soup.select("h3")

    # List comprehension to get text from the list of hemisphere h3 tags
    hemispheres = [name.text for name in hemispheres]

    # Initialize empty list to store dictionaries of hemisphere names 
    # and image links into later
    hemisphere_imgs = []

    # For each hemisphere, create dictionary entry, click on their links, 
    # get the url of the full image, and go back to the results page to 
    # click on the next hemisphere
    for index, value in enumerate(hemispheres):
        # String manipulation to store name without "Enhanced"
        hemisphere_imgs.append({"name": " ".join(value.split()[:-1])})

        # Return list of elements that contain name of hemisphere (should only
        # be one, but links.find_by_partial_text fails when using Firefox, so
        # this is the alternative solution for compatibility in both)
        hemisphere_link = browser.find_by_text(value)
        hemisphere_link[0].click()

        # Grab the new page's HTML and parse using beautiful soup
        html = browser.html
        soup = BeautifulSoup(html, "lxml")

        # Get image url, add to dictionary
        img_url = (
            f"https://astrogeology.usgs.gov"
            f"{soup.select_one('img.wide-image')['src']}"
        )
        hemisphere_imgs[index]["url"] = img_url

        # Go back to page with all hemispheres, reload the html
        browser.back()
        html = browser.html
        soup = BeautifulSoup(html, "lxml")

    # End browser instance
    browser.quit()

    # Get date for the last time database was updated
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "latest_news": latest_news,
        "featured_img": image_of_week,
        "facts": html_facts_table,
        "hemispheres": hemisphere_imgs,
        "last_updated": last_updated
    }

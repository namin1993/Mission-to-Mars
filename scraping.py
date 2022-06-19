# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_dict": hemisphere(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:

        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    try:
        # Using Pandas Dataframe to scrape a table from a website
        df = pd.read_html('https://galaxyfacts-mars.com')[0] # The Pandas function read_html() specifically searches for and returns a list of tables found in the HTML.
    
    except BaseException:
        return None

    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

### Hemispheres
def hemisphere(browser):

    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    mars_soup = soup(html, 'html.parser')
    mars_list = mars_soup.find_all('div', class_='item')

    for mars_obj in mars_list:
        hemispheres = {}
        
        # Click on each link
        planet_url_rel = mars_obj.find('a', class_='itemLink').get('href')
        planet_url = f'https://marshemispheres.com/{planet_url_rel}'
        browser.visit(planet_url)
        
        html = browser.html
        planet_soup = soup(html, 'html.parser')
        
        # Select title
        title = planet_soup.find('h2', class_='title').get_text()
        
        # Get first list element, click, and Select jpg src
        img_ul = planet_soup.find('ul')
        sample_jpg_src = img_ul.find('a').get('href')
        
        # Append title and image link into dictionary
        hemispheres['img_url'] = f'https://marshemispheres.com/{sample_jpg_src}'
        hemispheres['title'] = title
        
        # Append dictionary item into list
        hemisphere_image_urls.append(hemispheres)

        # Go back to main browser
        browser.back()

    # 4. Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
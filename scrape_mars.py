#dependencies
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import time

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=True)


def scrape_info():
    browser = init_browser()

    # set up all urls needed to be visited
    nasa = 'https://mars.nasa.gov/news/' 
    nasa_image_search_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    mars_facts_url = 'https://space-facts.com/mars/'
    ref_url = 'https://astrogeology.usgs.gov'
    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(nasa)
    browser.visit(nasa)
    time.sleep(1)


    # Scrape page into Soup
    html = browser.html
    soup = bs(html, 'lxml')

    #pulls info based on div information
    title = soup.select("div.content_title" )
    teaser = soup.select("div.article_teaser_body")

    #first article is a snippet on the header, pulls first actual article
    article_title = title[1].text 
    #pulls first teaser
    article_teaser = teaser[0].text

    #start splinter to go search the website
    browser.visit(nasa_image_search_url)   
    #looks for button that has full image, which is the featured photo
    browser.click_link_by_partial_text('FULL IMAGE')
    #presses next button to find a link to where the full image is stored
    browser.click_link_by_partial_text('more info')
    #final link press by href to find the actual image link
    browser.click_link_by_partial_href('/spaceimages/image')
    #return url where image is stored
    img_link = browser.url

    hemi_html = requests.get(hemisphere_url)
    hemi_soup = bs(hemi_html.text, 'lxml')
    #establish list that will be appeneded with the img urls
    hemisphere_image_urls = []
    #have it cycle for the amount of hemispheres from the soup
    for hemi in hemi_soup.find_all('h3'):
        #start from intial website
        browser.visit(hemisphere_url)
        #find the name of the hemisphere via soup
        hemisphere = hemi.text
        #click by name
        browser.click_link_by_partial_text(hemisphere)
        #use beautiful soup again to find the img link
        hemisphere_page = requests.get(browser.url)
        hemi_soup = bs(hemisphere_page.text, 'lxml')
        #finds the image, extracts the src, references the original website to make a full url
        image =hemi_soup.find('img', class_ = 'wide-image')
        image_url = ref_url+image['src']
        #creates dictionary with the found data
        hemi_dict = {"title":hemi.text.replace(' Enhanced',''),
                    "img_url":image_url}
        #drops into created list
        hemisphere_image_urls.append(hemi_dict)

    #set up new url for pandas table scraping
    tables = pd.read_html(mars_facts_url)
    #set dataframe for the table
    df = tables[1]
    #sets index of the data
    df.set_index("Mars - Earth Comparison",inplace=True)
    #convert to html table
    table = df.to_html(header = 'true')
    table = table.replace("\n","")

    mars_data = {
        'article_title':article_title,
        'article_teaser':article_teaser,
        'table':table,
        'hemisphere_image_urls': hemisphere_image_urls,
        'img_link':img_link
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data 

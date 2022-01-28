#!/usr/bin/env python
# coding: utf-8

# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd 
import datetime as dt
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo


# 1.	Initialize the browser.
# 2.	Create a data dictionary.
# 3.	End the WebDriver and return the scraped data.
# Let's define this function as "scrape_all" and then initiate the browser.
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    # in headless mode. All of the scraping will still be accomplished, but behind the scenes.
    browser = Browser('chrome', **executable_path, headless=True)
    # tells Python that we'll be using our mars_news function to pull this data.
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_data(browser),
        "last_modified": dt.datetime.now()
    }
        # Stop webdriver and return data
    browser.quit()
    return data


 
# we'll be using the browser variable we defined outside the function
def mars_news(browser):
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    # url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)


    html = browser.html
    news_soup = soup(html, 'html.parser')
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # slide_elem
        # slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # news_title

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
        # news_p
    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    # url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)
    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()
    # full_image_elem

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='thumbimg').get('src')
        # img_url_rel
    except AttributeError:
        return None
    # If we look at our address bar in the webpage, we can see 
    # the entire URL up there already; we just need to add the first portion to our app.
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    # img_url
    return img_url


def mars_facts():

    try:
    # The Pandas function read_html() specifically searches for and 
    # returns a list of tables found in the HTML. By specifying an index of 
    # 0, we're telling Pandas to pull only the first table it encounters,
    # or the first item in the list. Then, it turns the table into a DataFrame.

        # df = pd.read_html('https://galaxyfacts-mars.com')[0]

        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
    # •	df.columns=['description', 'Mars', 'Earth'] Here, we assign columns 
    # to the new DataFrame for additional clarity.
    # •	df.set_index('description', inplace=True) By using the .set_index() 
    # function, we're turning the Description column 
    # into the DataFrame's index. inplace=True means that the updated index 
    # will remain in place, without having to reassign the DataFrame to a new variable.
    # Now, when we call the DataFrame, we're presented with a tidy, 
    # Pandas-friendly representation of the HTML table we were just viewing 
     # df
    except BaseException:
        return None
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # How do we add the DataFrame to a web application? Robin's web app is going to be an actual webpage
    # Pandas also has a way to easily convert our DataFrame back into HTML-ready code using the .to_html() function
    return (df.to_html(classes="table table-striped"))
# we can end the automated browsing session. This is an important line to 
# add to our web app also. Without it, the automated browser won't know to 
# shut down—it will continue to listen for instructions and use the computer's
# resources (it may put a strain on memory or a laptop's battery if left on).
#            We really only want the automated browser to remain active while
#            we're scraping data. It's like turning off a light switch when 
#            you're ready to leave the room or home. 
# browser.quit()
# we can't automate the scraping using the Jupyter Notebook. 
# To fully automate it, it will need to be converted into a .py file.


# This last block of code tells Flask that our script is complete and ready for action. 
# The print statement will print out the results of our scraping to our terminal 
# after executing the code.

# get the mars hemisphere data
def hemisphere_data(browser) :
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars/'

    browser.visit (url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    #  Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    #find all images
    all_imgs = img_soup.find_all('div', class_='description')

    # for each link on the main page loop and soup
    for image in all_imgs: 
    #   simulate clik on the first link
        browser.find_by_text(image.find('h3').text).click()
        img_url, title = hemisphere_scrape(browser.html)
        hemisphere_image_urls.append({"img_url": img_url, "title": title})
    #     go back to main page to process the next link
        browser.back() 
    # return the scraped data as a list of 
    # dictionaries with the URL string and title of each hemisphere image
    return(hemisphere_image_urls)

# do the scraping of img_url and title in this funcion and return them
def hemisphere_scrape(browser_html):
    # Parse the resulting html with soup
    img_soup = soup(browser_html, 'html.parser')
    try:
        #     get the title of the link that we want to visit
        title = img_soup.find('h2', class_ = "title").text
        #     get the img url searching for Sample text
        img_url = img_soup.select('li')[0].find('a', text="Sample").get('href')
    #     create a dictionary that holds the title and the img url
    except AttributeError:
        title = None
        img_url = None 
    return(img_url, title)

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

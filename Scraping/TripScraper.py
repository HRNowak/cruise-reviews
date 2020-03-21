from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import time
from random import randint
from bs4 import BeautifulSoup
from simp_pickle import load_pickle, save_pickle
from time import sleep
import numpy as np
import requests
import pandas as pd
from sys import exit

class TripScraper:
    """Class that handles all the steps of review scraping.
    Warning: Depending on the number of ships/reviews to scrape, the code can take hours to download all the information.

    Flow:
    1 - Instantiate class: 2 parameters required:
            - list_of_dest_urls: A list of urls (strings) for the pages that have the list of ships for each destination.
            - driver: The path to the chrome driver file. You can find all versions of Chrome Drivers at 'https://chromedriver.chromium.org/downloads'
    2 - Scrape list of ships for those destinations using the 'ships_scrape' method. This will generate a dictionary with every ship url.
    3 - Once step 2 is completed, you can call the reviews_scrape method to scrape reviews and place them in a DataFrame.

    Saving your progress:
    1) You can interrupt the process at any point. The object will store data up until the last ship that was fully scraped.
    Progress can be saved on the hard drive by calling the save_progress method.
    2) To resume scraping after the programme has closed, used the load_progress method.

    Updating object elements:
        - list_of_dest_urls: The update_destinations method takes a list and turns it into a progress dictionary.
        - driver: The path to the driver can be updated by simply typing object.driver = '/new_location/chromedriverfilename'
        - ship_progress: An empty dictionary is created every time TripAdvisor object is instantiated. This will be updated with either the ship_scrape or the load_progress methods.
        - reviews: An empty DataFrame is created every time TripAdvisor object is instantiated. This will be updated with either the reviews_scrape or the load_progress methods.
    """

    def __init__(self, list_of_dest_urls = [], driver = './chromedriver'):
        """1) list_of_dest_urls: A list of urls (strings) for the pages that have the list of ships for each destination. eg https://www.tripadvisor.co.uk/Cruises-g147237-Caribbean-Cruises
        2) driver: Path to Chrome driver file. You can find all versions of Chrome Drivers at 'https://chromedriver.chromium.org/downloads' """
        #Creates dictionary with every destination url as a key.
        self.destinations_progress = {}
        self.update_destinations(list_of_dest_urls)
        #Creates empty dictionary. This can be updated calling the ship_scrape method.
        self.ship_progress = {}
        self.data_list = ['reviews_ship_link','review_user_contributions','review_user_helpful_votes'
                             ,'review_links','review_user_date','review_user_link','review_ranking'
                            ,'review_title','review_content','review_meta','review_user_hometown']
        self.reviews = pd.DataFrame()
        self.driver = driver

    def update_destinations(self,list_of_dest_urls):
        """Takes a list of URLs as a input and creates a new destination dictionary with all values set to False"""
        self.destinations_progress = {url: False for url in list_of_dest_urls}

    def save_progress(self,pickle_file = 'progress_dictionaries.pkl', csv_file = 'reviews.csv'):
        """Saves progress on your hard drive. 2 files are created (see below). The names for these files can be passed as method parameters.
        - pickle_file: Path for pickle containing ship_progress & destionation_progress dictionaries.
        - csv_file:  Path for csv file containing all reviews."""
        save_pickle((self.destinations_progress,self.ship_progress),pickle_file)
        self.reviews.to_csv(csv_file)

    def load_progress(self,pickle_file,csv_file):
        info = load_pickle(pickle_file)
        self.destinations_progress = info[0]
        self.ship_progress = info[1]
        self.reviews = pd.read_csv(csv_file, index_col=0)

    def ships_scrape(self):
        """Opens each destination url on Chrome and scrapes every ship's url. These urls are saved as keys in the ship_progress dictionary.
        The value to each element is set to False meaning that the reviews for those ships haven't been scraped yet.
        """
        urls = [url for url in self.destinations_progress.keys() if self.destinations_progress[url] == False]
        driver = webdriver.Chrome(self.driver)
        ship_set = set()
        for url in urls:
            # goes to url and wait to load
            driver.get(url)
            for x in range(1000):
                # wait for page to load
                sleep(2)
                soup = BeautifulSoup(driver.page_source, 'lxml')
                #finds all ships
                ships = soup.find_all('div', class_='cruises-cruises-list-results-Result__listingWrapper--3yL9e')
                #adds each ship's link into a set. If it can't, it carries on with the next one.
                for ship in ships:
                    try:
                        link = ship.find('a').get('href')
                        if isinstance(link,str):
                            ship_set.add(link)

                    except:
                        pass
                try:
                    button = driver.find_element_by_class_name("ui_button.nav.next.primary")
                    button.click()
                except:
                    break
            for link in ship_set:
                self.ship_progress[link] = False
            self.destinations_progress[url] = True
        driver.close()


    def reviews_scrape(self):
        # defining urls to scrape:
        urls = [url for url in self.ship_progress.keys() if self.ship_progress[url]!=True]
        # Open Chrome Session
        driver = webdriver.Chrome(self.driver)
        # Iterate through list of URLs
        for url in urls:
            # setting counters and clean dictionary
            reviews_dict = {field :[] for field in self.data_list}
            cruise = url.split('-')[-1]
            print('Starting with {}...'.format(cruise))
            # Get URL and wait a bit
            driver.get('https://www.tripadvisor.co.uk' + url + '#ship_reviews')
            languages = driver.find_elements_by_class_name(
                'ui_radio.location-review-review-list-parts-ReviewFilter__filter_row--p0z3u')
            for lang in languages:
                if 'English' in lang.text:
                    lang.click()
            sleep(randint(0, 2))
            # Extract Ship data (only once)
            soup0 = BeautifulSoup(driver.page_source, 'lxml')
            #MAYBE ERASE extract_ship_data(soup0, url)
            # Iterate through each page (stop when page has no "next" button)
            has_next = True
            while has_next:
                sleep(2)
                try:
                    # This try stops the script from breaking with ships with no reviews
                    # Click on 'Read More' button to expand all reviews
                    reference = driver.find_element_by_class_name(
                        'social-member-event-MemberEventOnObjectBlock__event_type--3njyv')
                    driver.execute_script("arguments[0].scrollIntoView();", reference)
                    succeeded = False
                    while succeeded == False:
                        sleep(1)
                        try:
                            button_expand = driver.find_element_by_class_name(
                                "location-review-review-list-parts-ExpandableReview__cta--2mR2g")
                            button_expand.click()
                            succeeded = True
                        except:
                            succeeded = False

                    # Soups, gets list of reviews and extract data for each one of them
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    reviews = soup.find_all('div', {
                        'class': 'location-review-card-Card__ui_card--2Mri0 location-review-card-Card__card--o3LVm location-review-card-Card__section--NiAcw'})

                    for review in reviews:
                        extract_review_data(review, url,reviews_dict)
                    try:
                        buttonNext = driver.find_element_by_class_name("ui_button.nav.next.primary")
                        buttonNext.click()
                    except:
                        break
                except:
                    # If no reviews were found, stop iterating on this ship a go to the next one,
                    break

            try:
                #updating
                self.reviews = pd.concat([self.reviews, pd.DataFrame(reviews_dict)])
                self.ship_progress[url] = True

            except:
                exit()
            print('Finished with {}.'.format(cruise))
        driver.close()






def extract_review_link(review):
    try:

        return review.find('div', {'class': 'location-review-review-list-parts-ReviewTitle__reviewTitle--2GO9Z'}
                           ).find('a').get('href')
    except:
        return np.NaN


def extract_review_user_date(review):
    try:
        return review.find('div', {'class': 'social-member-event-MemberEventOnObjectBlock__event_type--3njyv'}
                           ).text.replace(' wrote a review ', '|')
    except:
        return np.NaN


def extract_review_user_link(review):
    try:
        return review.find('div', {'class': 'social-member-event-MemberEventOnObjectBlock__event_type--3njyv'}
                           ).find('a').get('href')
    except:
        return np.NaN


def extract_review_user_contributions(review):
    try:
        return review.find_all('span', {'class': 'social-member-MemberHeaderStats__bold--3z3qh'}
                               )[0].text
    except:
        return np.NaN


def extract_review_user_helpful_votes(review):
    try:
        return review.find_all('span', {'class': 'social-member-MemberHeaderStats__bold--3z3qh'}
                               )[1].text
    except:
        return '0'


def extract_review_ranking(review):
    try:
        return review.find('div', {'class': 'location-review-review-list-parts-RatingLine__bubbles--GcJvM'}
                           ).find('span').get('class')[1].replace('bubble_', '')
    except:
        return np.NaN


def extract_review_title(review):
    try:
        return review.find('div', {'class': 'location-review-review-list-parts-ReviewTitle__reviewTitle--2GO9Z'}
                           ).text
    except:
        return np.NaN


def extract_review_content(review):
    try:
        return review.find('q', {'class': 'location-review-review-list-parts-ExpandableReview__reviewText--gOmRC'}
                           ).text
    except:
        return np.NaN


def extract_review_meta(review):
    try:
        string = ''
        metas = review.find_all('div', {'class': 'location-review-review-list-parts-EventDetails__event_key--2XaDW'})
        for meta in metas:
            string += (meta.text + '|')
        return string
    except:
        return np.NaN


def extract_review_user_hometown(review):
    try:
        return review.find('span', {'class': 'default social-member-common-MemberHometown__hometown--3kM9S small'}).text
    except:
        return np.NaN


def extract_review_data(review, url,reviews_dict):
    """Accepts individual review as input and saves review's data into different lists"""
    # Get review link
    link = extract_review_link(review)
    # check if already in list
    if link == np.NaN or link not in reviews_dict['review_links']:
        reviews_dict['reviews_ship_link'].append(url)
        reviews_dict['review_user_contributions'].append(extract_review_user_contributions(review))
        reviews_dict['review_user_helpful_votes'].append(extract_review_user_helpful_votes(review))
        reviews_dict['review_links'].append(link)
        reviews_dict['review_user_date'].append(extract_review_user_date(review))
        reviews_dict['review_user_link'].append(extract_review_user_link(review))
        reviews_dict['review_ranking'].append(extract_review_ranking(review))
        reviews_dict['review_title'].append(extract_review_title(review))
        reviews_dict['review_content'].append(extract_review_content(review))
        reviews_dict['review_meta'].append(extract_review_meta(review))
        reviews_dict['review_user_hometown'].append(extract_review_user_hometown(review))
    else:
        pass


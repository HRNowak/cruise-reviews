# Cruise Review Classification


**General Assembly Data Science Immersive - Final Capstone Project** 

The purpose of this project is to create a machine learning classifier to help digital marketers and community managers detect negative reviews or comments online. In this particular application, I focus on the cruise industry due to the richness of aspects that can be covered in each review.

## Background and problem statement

From a marketing perspective, the twenty-first century is marked by introduction of online channels as a means of communication between companies and customers. The novelty of this channel is that this 'conversation' stopped being predominantly one-sided (companies talking to potential customers) and now users have a much larger share of voice.

Initially some companies saw this shift as a threat to the way things were done, but it is clear nowadays that this conversation isn't only necesary, but it also poses an opportunity for companies to receive feedback and improve their products and services.

In order to thrive in this new environment, brands need to monitor their presence online within a vast and complex  environment. Crucial to success is to be able to do this systematicallt and swiftly, and machine learning can help doing that in many ways. 

## Project Overview

### Scraper

The first stage of this project consisted of scraping over 9,000 reviews from TripAdvisor. This website is particularly challenging to scrape due to, among other reasons:
- the limited number of reviews per page
- the variety and inconsistency of elements included in every review (meta data)
- the need to interact with every page to expand the content of every review and to filter out other languages
- the speed of the page to respond to this interactions.
In order to overcome this, I created a class to streamline the whole process with a robust code. The objects belong to this class have the ability to keep track of any progress done and stop the process whenever needed without losing information. All progress can be easily stored on the hard drive and scraping can be resumed at a later time. 

### Classifier

The approach taken cosisted of testing different NLP techniques (sentiment analysis, tf-idf, term frequencies and word counts) and various classifying algorithms, including:
- KNeighbours
- Logistic Regression
- Decision Trees
- Naive Bayes
- Random Forest
- Bagging Classifier
- Ada Boosting
- Gradient Boosting
- SVM
- Multilayer Perceptron (MLP)

The resulting model is a Logistic Regression that combines sentiment analysis scores with TF-IDF matrices focusing on a small portion of adjectives, verbs and nouns. With a total of 672 features, the algorithm achieved a 92.5 AUC score and an 86% accuracy on test data. The model is further adjusted to improve the recall of bad reviews. 

## Structure

**- Scraping (Folder):**
  - TripScraper.py: Includes scraper class and other functions. 
  - driver.exe: Chrome Driver required to use Sellenium. You can find more drivers available on https://chromedriver.chromium.org/downloads.
  - simp_pickle.py: Includes streamlined functions for pickling and loading Python elements.
  - TripScraper Instructions.ipynb: Step by step explanation of how to use the TripScraper.
  - progress_dictionaries.pkl, reviews.csv: Examples of how reviews and overall progress is stored.

**Other Files**
- data_cleaning_EDA.ipynb:Includes all the steps followed to clean the data and extract necessary features.
- stage1_algorithm_selection.ipynb: Includes testing different algorithms and parameters with a fixed and comprehensive set of features.
- stage2_feature_selection.ipynb: In this file I test different combinations of features to find the optimal set.
- stage3_model_analysis_and_optimisation: This includes the analysis of the final model and final adjustsments. 

## What's next?
I am now looking to expand this project by training an algorithm to label reviews based on the aspects of the ship mentioned, such as staff, amenities, cabin, food, etc.

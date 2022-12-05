"""
        Finding or Building a Corpus
        -----------------------------

        Author:
            Nebil Weber
            Zach Allen

        NetID:
            nxw180009
            zma180000

        Class:
            CS 4395.001 - Human Language Technologies - F22
        """

# Library Imports
import os
import pickle
from bs4 import BeautifulSoup
import requests
import validators
import urllib.request
import re
import pathlib
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords


def crawler(link):
    """
        Function that starts with a URL representing a topic
        (a sport, your favorite film, a celebrity, a political issue, etc.)
        and craws finding relevant links.

        Args:
            link: Starting url

        Returns:
            A list of at least 15 relevant URLs. The URLs can
            be pages within the original domain but should have
            a few outside the original domain.
        """

    r = requests.get(link)
    url_list = []  # list to store urls

    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    counter = 0

    print("\nStarter URL: " + link)
    print("\nRelevant URLs: ")

    # Print relevant URLs and append each one to a list
    for link in soup.find_all('a'):
        url_list.append((str(link.get('href'))))
        print("\t" + str(counter + 1) + ". " + link.get('href'))
        counter += 1
        if counter > 49:
            break

    return url_list


def scraper(url_list, link):
    """
        Function to loop through the URLs and scrape all text off each page
        and store each page’s text in its own file.

        Args:
            url_list: list of relevant urls
            link:     Starting url

        Returns:
            Pass
        """

    # function to determine if an element is visible - from Dr. Mazidi's slides
    def visible(element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', str(element.encode('utf-8'))):
            return False
        return True

    counter = 1

    for i in range(len(url_list)):
        if url_list[i][0] == '/':
            url_list[i] = link + url_list[i]
        if validators.url(url_list[i]):
            try:
                html = urllib.request.urlopen(url_list[i])
            except:
                pass
            soup = BeautifulSoup(html, "html.parser")
            data = soup.findAll(text=True)
            result = filter(visible, data)
            temp_list = list(result)  # list from filter
            temp_str = ' '.join(temp_list)

            # create folder if it doesn't exist
            if not os.path.exists("Scrape"):
                os.mkdir("Scrape")

            # file names
            fileName = "Scrape/Scrape-Text"

            if len(temp_str) > 1000:
                # open and write to the file
                f = open(pathlib.Path.cwd().joinpath(fileName + str(counter) + ".txt"), "w")
                f.write(str(temp_str.encode("utf-8")))

                counter += 1  # update counter

            if counter > 15:  # break at 15
                break


def formatText():
    """
        Function to clean up the text from each file
        and store each page’s text in its own file.

        Returns:
            Pass
        """

    counter = 1

    # folder path
    dir_path = r'Scrape'

    fileCount = 0

    # Iterate directory and count number of files
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            fileCount += 1

    for i in range(1, fileCount + 1):
        with open(pathlib.Path.cwd().joinpath("Scrape/Scrape-Text" + str(i) + ".txt"), 'r') as f:
            # delete newlines and tabs
            data = f.read().replace('\n', '').replace('\t', ' ')

            # Extract sentences with NLTK’s sentence tokenizer
            tokenList = sent_tokenize(data)

            # create folder if it doesn't exist
            if not os.path.exists("CleanScrape"):
                os.mkdir("CleanScrape")

            # file names
            fileName = "CleanScrape/ModifiedScrape-"

            # Write the sentences for each file to a new file
            newF = open(pathlib.Path.cwd().joinpath(fileName + str(counter) + ".txt"), "w")
            for t in range(len(tokenList)):
                if '\\' not in tokenList[t]:
                    newF.write(str(tokenList[t].encode("utf-8")))
            counter = counter + 1


def importantTerms():
    """
        Function to extract at least 25 important terms from
        the files using an importance measure such as term frequency,
        or tf-idf

        Return:
            entireText: all the text in each of the 15 files
        """

    entireText = ""

    for i in range(15):
        # Put all the text in each of the 15 files into entire text
        with open(pathlib.Path.cwd().joinpath("CleanScrape/ModifiedScrape-" + str(i + 1) + ".txt"), 'r') as f:
            # lower-case everything
            text = f.read().lower()
            entireText += text + " "

    # remove stopwords and punctuation
    stop_words = stopwords.words('english')
    tokens = word_tokenize(entireText)
    tokens = [w for w in tokens if w.isalpha() and w not in stop_words]

    unigrams = tokens
    unigram_dict = {token: unigrams.count(token) for token in set(unigrams)}

    # Sort the dictionary
    sorted_unigrams = sorted(unigram_dict.items(), key=lambda x: x[1], reverse=True)

    # print top 40 terms
    print("\nTop 40 most common terms in all 15 pages:")
    for counter in range(2, 42):
        print("{}.".format(counter - 1), sorted_unigrams[counter])

    return entireText


def kb(top10Terms, entireText):
    """
        Function build a searchable knowledge base of facts
        and creates a pickle dic file.

        Args:
            top10Terms: Top 10 important terms
            entireText: All the text in each of the 15 files

        Returns:
            Pass
        """

    # Extract sentence from the text
    sentences = sent_tokenize(entireText)

    # list to hold sentences that have the 10 terms
    terms = []

    # key = term, values = sentences
    termsDict = {"share": [], "valorant": [], "game": [], "players": [], "team": [],
                 "surface": [], "communities": [], "rioters": [], "priscila": [], "challenge": []}

    # if a sentence from entire text has that term, add it to a list and append that list into the dictionary.
    for term in top10Terms:
        for sent in sentences:
            if term in sent:
                terms.append(sent)
        termsDict[term] += terms
        terms.clear()  # Clear the list for the next iteration

    # Pickle dict and read in the pickle file
    pickle.dump(termsDict, open(pathlib.Path.cwd().joinpath('my_10_terms_dict.p'), 'wb'))
    knowledge_base = pickle.load(open('my_10_terms_dict.p', 'rb'))

    print("\nThe knowledge base is: ")

    # Iterate over key/value pairs in dict and print them
    for key, value in knowledge_base.items():
        print(key, ' : ', value)
        print("\n")


# main function
def main():
    url = 'https://www.riotgames.com'  # starting url
    urlData = crawler(url)
    scraper(urlData, url)
    formatText()
    text = importantTerms()

    top10Terms = ['share', 'valorant', 'game', 'players', 'team', 'surface', 'communities', 'rioters', 'priscila',
                  'challenge']

    kb(top10Terms, text)


# start with main
if __name__ == "__main__":
    main()

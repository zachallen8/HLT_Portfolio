"""
        Ngrams Program2
        ---------------

        Author:
            Nebil Weber
            Zach Allen

        NetID:
            nxw180009
            zma180000

        Class:
            CS 4395.001 - Human Language Technologies - F22
        """

# library imports
import pickle
import sys
from nltk import word_tokenize
from nltk.util import ngrams


def readpickledDict():
    """
            Function reads in all 6 pickled dictionaries

            Returns:
                a master list of all the ngrams
            """

    allNgrams = {}                                  # list of all Ngrams
    languages = ["English", "French", "Italian"]    # list of languages

    # loop through pickle files
    for language in languages:
        unigramDict = f"{language}_unigram_dict.p"
        bigramDict = f"{language}_bigram_dict.p"

        # read in unigram and bigram from file
        unigram = pickle.load(open(unigramDict, "rb"))
        bigram = pickle.load(open(bigramDict, "rb"))

        # store in a dict using the language and either unigram or bigram as keys
        allNgrams[language] = {
            "unigram": unigram,
            "bigram": bigram,
        }

    return allNgrams


def getHighestProb(line, masterDict, vocabCount):
    """
            For each line in the test file, The function calculates probability for each language.

            Args:
                line: A sentence from the test data file
                masterDict: Master list of all the Ngrams
                vocabCount: The total vocab count

            Returns:
                The language with the highest probability
            """

    tokens = word_tokenize(line)          # tokenzie the line
    bigramList = list(ngrams(tokens, 2))  # creates bigram list
    english, french, italian = 1, 1, 1    # initiate the probabilities for the languages

    # for each bigram, calculate the probability for all three languages
    for i in bigramList:

        english *= (masterDict["English"]["bigram"].get(i, 0) + 1) / (masterDict["English"]["unigram"].get(i[0], 0) + vocabCount)

        french *= (masterDict["French"]["bigram"].get(i, 0) + 1) / (masterDict["French"]["unigram"].get(i[0], 0) + vocabCount)

        italian *= (masterDict["Italian"]["bigram"].get(i, 0) + 1) / (masterDict["Italian"]["unigram"].get(i[0], 0) + vocabCount)

    # get the max probability
    maximumProbability = max(english, french, italian)

    # return the language that the max_probability corresponds to
    if maximumProbability == french:
        return "French"
    elif maximumProbability == english:
        return "English"
    else:
        return "Italian"


def TestFileProbability(filename):
    """
            The function just writes the language with the highest probability to a file

            Args:
                filename: test data file

            """

    # master list of all the ngrams for every language
    masterDict = readpickledDict()

    # get the total vocab count
    # the total vocabulary size (add the lengths of the 3 unigram dictionaries).
    vocabCount = len(masterDict["English"]["unigram"]) + len(masterDict["French"]["unigram"]) + len(
        masterDict["Italian"]["unigram"])

    filename = open(filename)      # open file name
    lines = filename.readlines()   # get the list of test lines
    filename.close()               # close file name

    # open file to write
    output_file = open("highestProbability", "w+")

    # make a guess and write to the file
    counter = 1

    # iterate through each sentence (line)
    for line in lines:
        highestProbability = getHighestProb(line, masterDict, vocabCount)   # get the highest probability
        output_file.write(f"{counter} {highestProbability}\n")              # write to the file
        counter += 1                                                        # increment counter

    pass


def verification(myClassifications, correctClassifications):
    """
            Function to Compute and the accuracy as the percentage of correctly
            classified instances in the test set.

            Args:
                myClassifications: my classifications
                correctClassifications: the correct classifications

            Returns:
                None, it prints the accuracy as well as the line numbers of the
                incorrectly classified items.
            """

    # open the files
    myFile = open(myClassifications)
    solutionFile = open(correctClassifications)

    # read the lines for each file into a list
    myLine = myFile.readlines()
    correctLine = solutionFile.readlines()

    # list to store the line numbers for incorrectly classified items
    incorrectlyClassified = []

    # counters
    correctClassification = 0

    # get the corresponding line for both instances
    for i, j in zip(myLine, correctLine):
        # split it
        split = j.split()

        # if the instances are the same, increment correctClassification
        if i == j:
            correctClassification += 1
        # else, append to incorrectlyClassified list
        else:
            incorrectlyClassified.append(int(split[0]))

    # print statistics
    print("\nAccuracy for Correct Classifications:", correctClassification / len(correctLine) * 100, "%")
    print("\nLine numbers for Incorrect Classifications:", incorrectlyClassified)

    pass


# run main (Starting method of the program)
if __name__ == '__main__':

    """
                   Start function of program 2.

                   Args:
                       Test data set (Langid.test)
                       
                   """

    if len(sys.argv) < 2:
        print('Please enter a filename as a system arg')

    TestFileProbability(sys.argv[1]) # gets the language with the highest probability
    verification("highestProbability", "Langid.sol")

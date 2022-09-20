from gzip import READ
import os
import sys 
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from random import random, seed
from random import randint

def main():
    raw_text = '' #raw text variable

    def preprocess(tokenList): #function for preprocessing raw_text
        tokenListLower = [t.lower() for t in tokenList]
        filteredTokens = [i for i in tokenListLower if i.isalpha() and i not in stopwords.words('english') and len(i) > 5] #filters tokens based on given criteria
        wnl = WordNetLemmatizer()
        lemmas = [wnl.lemmatize(i) for i in filteredTokens] #lemmatized tokens
        uniqueLemmas = list(set(lemmas))
        tags = nltk.pos_tag(uniqueLemmas) #uses pos tagger
        print(tags[:20])
        nounList = [i[0] for i in tags if i[1] == 'NN'] #gets list of nouns from pos tagger
        print("Length of filtered tokens list: " + str(len(filteredTokens)))
        print("Length of nouns list: " + str(len(nounList)))
        return filteredTokens, nounList #returns token list and noun list
    
    def guessingGame(wordList): #function for guessing game
        points = 5
        seed(1234)
        randomWord = wordList[randint(0, len(wordList)-1)] #gets random word
        guessed = []
        print("\nLet's play a word guessing game! You start with 5 points.")
        print("Gain a point for a correct guess, lose a point for an incorrect guess. End game by entering \'!\'.")
        outputWord = list(randomWord)
        for i in range(len(outputWord)): #outputs blanks
            outputWord[i] = '_'
        listToString = ' '.join([str(elem) for elem in outputWord]) #joins list for word to be output
        print(listToString)
        print('')
        guess = ''
        while guess != '!' or points > -1 or '_' in outputWord: #loops until game over
            guess = input("Guess a letter: ")
            if guess == '!':
                print("Exit command entered. Final score is: " + str(points))
                exit()
            if guess in guessed:
                print("Letter has alraeady been guessed. Try again.")
                continue
            if len(guess) > 1:
                print("Invalid guess. Try again.")
                continue
            if guess in randomWord: #runs if letter is correctly guessed
                points = points + 1
                print("Right! Score is " + str(points))
                guessed.append(guess) #adds letter to guessed list
                for i in range(len(randomWord)):
                    if(randomWord[i] == guess):
                        outputWord[i] = guess
                    listToString = ' '.join([str(elem) for elem in outputWord])
                print(listToString)
                if '_' not in listToString: #runs if word is correctly guessed
                    print("You solved it! Final score is: " + str(points))
                    exit()
            else: #runs if letter is incorrect
                points = points - 1
                if points < 0: #runs if user runs out of points (<0)
                    print("You lose. Sorry! Word was " + randomWord)
                    exit()
                guessed.append(guess)
                print("Sorry, guess again. Score is " + str(points))
                print(listToString)

    if len(sys.argv) < 2: #prints error message if no sysarg
        print('Please pass \'anat19.txt\' as a sysarg.')
        exit()
    else: #runs with sysarg .txt file
        fp = sys.argv[1]
        filepath = fp
        with open(os.path.join(os.getcwd(), filepath), 'r') as f:
            text_in = f.read()
        raw_text = text_in

    tokens = word_tokenize(raw_text)
    sets = set(tokens)
    print("Lexical diversity: %.2f" % (len(sets) / len(tokens))) #prints lexical diversity
    tokens, nouns = preprocess(tokens)
    nounCount = {}
    for i in nouns:
        nounCount.update({i: tokens.count(i)})
    commonNoun = dict(sorted(nounCount.items(), key=lambda item: item[1]))
    commonNoun = dict(reversed(list(commonNoun.items())))
    print(list(commonNoun.items())[:50]) #prints first 50 commonly used nouns
    commonNounList = list(commonNoun)[:50]

    guessingGame(commonNounList) #runs guessing game method

if __name__ == "__main__":
    main()
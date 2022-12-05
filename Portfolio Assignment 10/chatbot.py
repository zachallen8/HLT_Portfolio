# ----------------------------------------------------------------------------------
#                           Import Python modules
# ----------------------------------------------------------------------------------
import json
import random
import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import tflearn
import tensorflow as tf
from pymongo import MongoClient
from colorama import Fore, Style
import pickle
import pathlib

stemmer = LancasterStemmer()


# tokenize sentence and stem the words
def cleanSentence(sentence):
    sentence = nltk.word_tokenize(sentence)
    sentence = [stemmer.stem(word.lower()) for word in sentence]
    return sentence


# return bag of words array: 0 or 1 for each word in the bag that
# exists in the sentence
def bow(sentence, words, debug=False):
    sentence_words = cleanSentence(sentence)

    # array the size of the word array loaded in from the model
    bag = [0] * len(words)

    # assign a 1 to each bag of words array element that matches a word from the model
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                # for debugging purposes
                if debug:
                    print("found in bag: %s" % w)
    # return in numpy format
    return np.array(bag)


# function to classify the sentence
def classify(sentence):
    # get classification probabilities
    results = model.predict([bow(sentence, words)])[0]

    # remove predictions below the threshold
    results = [[i, r] for i, r in enumerate(results) if r > ERROR_THRESHOLD]

    # sort by probability
    results.sort(key=lambda x: x[1], reverse=True)

    return_list = []

    # (intent name, probability) pairs
    for r in results:
        return_list.append((classes[r[0]], r[1]))

    # return intent and probability tuple
    return return_list


# set threshold
ERROR_THRESHOLD = 0.25
context = {}


# function to respond back to the user
def response(sentence, firstName, userID='', debug=False):
    # dic to store user information
    userDict = {"userName": [], "userResponse": [], "botResponses": []}

    # store the result
    results = classify(sentence)

    # for debugging purposes
    if debug: print(results)

    if results:
        # check if the userID already exists
        if userID in context:
            # find tbe document matching the name of the classification
            doc = db.chatbot_intents.find_one(
                {'$and': [{'name': results[0][0]}, {'contextFilter': {'$exists': True, '$eq': context[userID]}}]})
            del context[userID]
            if debug: print(context)

        doc = db.chatbot_intents.find_one({'name': results[0][0]})

        # store userID with the context
        if 'contextSet' in doc and doc['contextSet']:
            if debug: print('contextSet=', doc['contextSet'])
            context[userID] = doc['contextSet']

        selection = random.choice(doc['responses'])  # store the response
        userDict['userName'] = firstName    # store the first name
        userDict['userResponse'] = sentence   # store the last name
        userDict["botResponses"] = selection  # store the bots response

        # if the document is found, select a response from the set of possible responses and return it to the user
        return print(Fore.GREEN + "Chatbot: " + Style.RESET_ALL + random.choice(doc['responses'])), userDict

    else:
        print('I dont know what we are talking about.')


# function to load the model
def load_model():
    # restore data structures
    data = pickle.load(open("training_data", "rb"))

    global words
    global classes

    words = data['words']
    classes = data['classes']
    train_x = data['train_x']
    train_y = data['train_y']

    # reset underlying graph data
    tf.compat.v1.reset_default_graph()

    # Build a neural network
    net = tflearn.input_data(shape=[None, len(train_x[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
    net = tflearn.regression(net)

    # load saved model
    model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
    model.load('./model.tflearn')
    return model


def delete_none(_dict):
    """Delete None values recursively from all the dictionaries, tuples, lists, sets"""
    if isinstance(_dict, dict):
        for key, value in list(_dict.items()):
            if isinstance(value, (list, dict, tuple, set)):
                _dict[key] = delete_none(value)
            elif value is None or key is None:
                del _dict[key]

    elif isinstance(_dict, (list, set, tuple)):
        _dict = type(_dict)(delete_none(item) for item in _dict if item is not None)

    return _dict


# function to parse the user model and write to a file
def formatUserModel(users):
    usersList = []

    # loop through user models
    for i in range(len(users['users'])):
        # get the name
        name = users['users'][i][0]['userName']
        usersList.append(name)

        # get each user response
        userResponse = users['users'][i][0]['userResponse']

        # get the bot response
        response = users['users'][i][0]['botResponses']

        # write to a file, then close
        f = open(pathlib.Path.cwd().joinpath(name + "_model.txt"), "a")
        if name in usersList:
            f.write("Name: " + name)
        else:
            continue

        f.write("\n userResponse: " + userResponse + "\n Response: " + response + "\n\n")
        f.close()

# function to interact with the chatbot
def prompt_user():
    print(Fore.YELLOW + 'Type "quit" to exit.', Style.RESET_ALL)
    print(Fore.YELLOW + "type 'switch to change users", Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX + "This is a chatbot that can talk to you about American football.",
          Style.RESET_ALL)
    print(Fore.GREEN + "ChatBot:" + Style.RESET_ALL, "What is your name?")
    print(Fore.LIGHTBLUE_EX + "User: " + Style.RESET_ALL, end="")
    name = input('')
    print(Fore.GREEN + "ChatBot:" + Style.RESET_ALL, "Hello, " + name)
    userInfo = {"users": []}

    # run infinite loop until user quits
    while (True):
        print(Fore.LIGHTBLUE_EX + name + ": " + Style.RESET_ALL, end="")
        line = input('')

        # quit if user chooses so
        if line.lower() == 'quit':
            break

        # switch users
        if line.lower() == 'switch':
            print(Fore.GREEN + "ChatBot:" + Style.RESET_ALL, "Hello new user, what is your name ")
            print(Fore.LIGHTBLUE_EX + "newUser: " + Style.RESET_ALL, end="")
            name = input('')
            print(Fore.GREEN + "ChatBot:" + Style.RESET_ALL, "Hello, " + name)
            print(Fore.LIGHTBLUE_EX + name + ": " + Style.RESET_ALL, end="")
            line = input('')

        # get a response
        userList = response(line, name, debug=False)

        # store user information
        userInfo['users'].append(userList)

    # delete none key values from the dic
    userInfo = delete_none(userInfo)

    Debug = False

    json_object = json.dumps(userInfo, indent=2)

    # create json object for testing purposes
    if Debug:
        print(json_object)

    formatUserModel(userInfo)



# ----------------------------------------------------------------------------------
#                           Main
# ----------------------------------------------------------------------------------

# connect to mongodb and set the Intents database for use
client = MongoClient('mongodb+srv://liinw:dypxo2-bukhix-hoptUg@cluster0.zubydkz.mongodb.net')
db = client.Intents

# load the model
model = load_model()

# start the chatbot agent
prompt_user()

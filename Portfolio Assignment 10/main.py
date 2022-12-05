# ---------------------------------------------------------------------------------#
#                           Chatbot Project                                        #
# ---------------------------------------------------------------------------------#
# Title       : Human Language Technologies ChatBot                                #
#                                                                                  #
# Purpose     : Create a chatbot using NLP techniques.                             #
#               The chatbot should be able to carry on a limited                   #
#               conversation in a particular domain (football)                     #
#               using a knowledge base.                                            #
#                                                                                  #
# Author      : Nebil Weber (nxw180009)                                            #
#               Zach Allen  (zma180000)                                            #
#                                                                                  #
#                                                                                  #
# Used for    : CS 4395.001                                                        #
#                                                                                  #
#                                                                                  #
# Tested on   : OS  - macOS                                                        #
#               IDE - Pycharm                                                      #
# ---------------------------------------------------------------------------------#

# ----------------------------------------------------------------------------------
#                           Import Python modules
# ----------------------------------------------------------------------------------
from pymongo import MongoClient
import numpy as np
import tflearn
import tensorflow as tf
import random
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import pickle
import nltk

nltk.download('punkt')
nltk.download('stopwords')

# ----------------------------------------------------------------------------------
#                               Database
# ----------------------------------------------------------------------------------

# connect to db and read in chatbot_intent collection
client = MongoClient('mongodb+srv://liinw:dypxo2-bukhix-hoptUg@cluster0.zubydkz.mongodb.net')
db = client.Intents

# store the collection
chatbot_intents = db.chatbot_intents


# ----------------------------------------------------------------------------------
#                               NLTK
# ----------------------------------------------------------------------------------

# stemmer object
stemmer = PorterStemmer()

words = []
classes = []
documents = []
english_stopwords = set(stopwords.words('english'))

# tokenizer will parse words and leave out punctuation
tokenizer = RegexpTokenizer("[\w']+")

# loop through each pattern for each intent
for intent in chatbot_intents.find():
    for pattern in intent['patterns']:
        tokens = tokenizer.tokenize(pattern)  # tokenize pattern
        words.extend(tokens)  # add tokens to word list
        # add tokens to document for specified intent
        documents.append((tokens, intent['name']))
        # add intent name to classes list
        if intent['name'] not in classes:
            classes.append(intent['name'])

# stem each word, change to lower case and remove duplicates
words = [stemmer.stem(w.lower()) for w in words if w not in english_stopwords]
# get unique words
words = sorted(list(set(words)))

# remove duplicate classes
classes = sorted(list(set(classes)))

Debug = False

# for debugging purposes
if Debug:
    print(len(documents), "documents")
    print(len(classes), "classes", classes)
    print(len(words), "words", words)

data_set = []

# create a sized array for output
output_empty = [0] * len(classes)

# training set, bag of words for each sentence
for document in documents:
    bag = []

    # stem the pattern words for each document element
    pattern_words = document[0]
    pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]

    # create a bag of words array
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    # output is a '0' for each intent and '1' for current intent
    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1

    data_set.append([bag, output_row])

    # for debugging purpose
    if Debug:
        print("bag", bag)
        print("output_row", output_row)
        print("data_set", data_set)

# ----------------------------------------------------------------------------------
#                  Machine Learning (Neural Network)
# ----------------------------------------------------------------------------------

# shuffle the features and convert to np.array
random.shuffle(data_set)

data_set = np.array(data_set)

# create training and test lists
train_x = list(data_set[:, 0])
train_y = list(data_set[:, 1])

# for debugging purpose
if Debug:
    print ("train_x", train_x)
    print ("train_y", train_y)


# reset underlying graph data
tf.compat.v1.reset_default_graph()

# Build neural network
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

# Define model and setup tensorboard
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')

# Start training (apply gradient descent algorithm)
model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True)
model.save('model.tflearn')

# save all the data
pickle.dump({'words': words, 'classes': classes, 'train_x': train_x, 'train_y': train_y}, open("training_data", "wb"))

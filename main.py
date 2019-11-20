import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
import glob
import re
import os
import numpy as np
import sys

"""
We sorted all words in whole data docs with it freq, 
and pick up the top 100 words.
Then choose the following eight words to be stopwords
by discussion.
"""
Stopwords = (
    "a", "and", "be", "in", 
    "is", "of", "the", "to"
)
stemmer = SnowballStemmer("english")

file_folder = 'dataset/*'

def finding_unique(words):
    words_unique = []
    
    for word in words:
        if word not in words_unique:
            words_unique.append(word)
    return words_unique

def finding_freq(words_unique):
    words_freq = {}
    for word in words_unique:
        words_freq[word] = words_unique.count(word)
    return words_freq

def remove_special_characters(text):
    regex = re.compile('[^a-zA-Z0-9\s]')
    text_returned = re.sub(regex, '', text)
    return text_returned


class Node:
    def __init__(self, docId, freq=None):
        self.freq = freq
        self.doc = docId
        self.nextval = None


class SlinkedList:
    def __init__(self, head=None):
        self.head = head

dict_global = {}
files_with_index = {}
linked_list_data = {}
doc_length = len(glob.glob(file_folder))

def doc_proc(op="Add"):
    global dict_global
    global files_with_index
    global linked_list_data
    idx = 1
    for file in glob.glob(file_folder):
        # print(file)
        fname = file
        file = open(file, "r")
        text = file.read()
        text = remove_special_characters(text)
        text = re.sub(re.compile('\d'), '', text)
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        words = [word for word in words if len(words) > 1]
        words = [word.lower() for word in words]
        words = [word for word in words if word not in Stopwords]
        words_stemmed = [stemmer.stem(x) for x in words]
        words_freq = finding_freq(finding_unique(words_stemmed))
        dict_global.update(words_freq)
        files_with_index[idx] = os.path.basename(fname)
        
        progress = (idx/doc_length)*100
        print("1/2\t", int(progress) , "%", end="\r")
        idx = idx + 1
    """
    for i, (key, value) in enumerate( sorted(dict_global.items(), key=lambda x: x[1]) ):
        print("%d, %s: %s" % (i, key, value))
    """
    unique_words_all = set(dict_global.keys())
    print()
    # index construct

    for word in unique_words_all:
        linked_list_data[word] = SlinkedList()
        linked_list_data[word].head = Node(1, Node)
    idx = 1
    for file in glob.glob(file_folder):
        file = open(file, "r")
        text = file.read()
        text = remove_special_characters(text)
        text = re.sub(re.compile('\d'), '', text)
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        words = [word for word in words if len(words) > 1]
        words = [word.lower() for word in words]
        words = [word for word in words if word not in Stopwords]
        words_stemmed = [stemmer.stem(x) for x in words]        ## doc words stem
        words_freq = finding_freq(finding_unique(words_stemmed))
        for word in words_freq.keys():
            linked_list = linked_list_data[word].head
            while linked_list.nextval is not None:
                linked_list = linked_list.nextval
            linked_list.nextval = Node(idx, words_freq[word])
        
        progress = (idx/doc_length)*100
        print("2/2\t", int(progress) , "%", end="\r")
        idx = idx + 1
print()
# no_found bug fix
try:
    doc_proc(op="Add")
    while True:
        options = input("\n" + \
        "1) Add documents\n" + \
        "2) Delete documents\n" + \
        "3) Enter query\n"
        )
        if options == '1':
            doc_proc(op="Add")
            print("Documents Added!")
            continue
        elif options == '2':
            doc_proc(op="Del")
            print("Documents Deleted!")
            continue
        elif options == '3':
            query = input('Enter your query:')
        else:
            print("Input Error!")
            continue
        query = word_tokenize(query)
        connecting_words = []
        cnt = 1
        no_found_cnt = 0
        different_words = []
        chk_not_at_first_place = 0
        for word in query:
             # remove special char in query
            word = remove_special_characters(word)
            if word.lower() != "and" and word.lower() != "or" and word.lower() != "not":
                words_stemmed = stemmer.stem(word.lower())  ## Query Stem
                different_words.append(words_stemmed)
            else:
                connecting_words.append(word.lower())

        # remove add if before not
        if(len(connecting_words)>=2) :
            for index, item in enumerate(connecting_words):
                if item == "and" and connecting_words[index+1] == "not":
                    connecting_words.pop(index)
        
        print(connecting_words)

        total_files = len(files_with_index)
        zeroes_and_ones = []
        zeroes_and_ones_of_all_words = []
        for word in (different_words):
            if word.lower() in set(dict_global.keys()):
                zeroes_and_ones = [0] * total_files
                linkedlist = linked_list_data[word].head
                print(word)
                while linkedlist.nextval is not None:
                    zeroes_and_ones[linkedlist.nextval.doc - 1] = 1
                    linkedlist = linkedlist.nextval
                zeroes_and_ones_of_all_words.append(zeroes_and_ones)
            else:
                zeroes_and_ones = [0] * total_files
                zeroes_and_ones_of_all_words.append(zeroes_and_ones)
                no_found_cnt = no_found_cnt + 1
                print(word, " not found")
        # print(zeroes_and_ones_of_all_words)
        # when all keywords not found
        if no_found_cnt == len(different_words):
            no_found_cnt = 0
            continue
        # when single keyword
        elif len(different_words) == 1 and no_found_cnt != 1:
            files = []
            lis = zeroes_and_ones_of_all_words[0]
            cnt = 1
            for index in lis:
                if index == 1:
                    files.append(files_with_index[cnt])
                cnt = cnt+1
            print(files)
        else:
            for word in connecting_words:
                word_list1 = zeroes_and_ones_of_all_words[0]
                word_list2 = zeroes_and_ones_of_all_words[1]
                if word == "and":
                    bitwise_op = [w1 & w2 for (w1, w2) in zip(
                        word_list1, word_list2)]
                    zeroes_and_ones_of_all_words.remove(word_list1)
                    zeroes_and_ones_of_all_words.remove(word_list2)
                    zeroes_and_ones_of_all_words.insert(0, bitwise_op)
                elif word == "or":
                    bitwise_op = [w1 | w2 for (w1, w2) in zip(
                        word_list1, word_list2)]
                    zeroes_and_ones_of_all_words.remove(word_list1)
                    zeroes_and_ones_of_all_words.remove(word_list2)
                    zeroes_and_ones_of_all_words.insert(0, bitwise_op)
                elif word == "not":
                    bitwise_op = [not w1 for w1 in word_list2]
                    bitwise_op = [int(b == True) for b in bitwise_op]
                    zeroes_and_ones_of_all_words.remove(word_list2)
                    zeroes_and_ones_of_all_words.remove(word_list1)
                    bitwise_op = [w1 & w2 for (w1, w2) in zip(
                        word_list1, bitwise_op)]
            zeroes_and_ones_of_all_words.insert(0, bitwise_op)

            files = []
            # print(zeroes_and_ones_of_all_words)
            lis = zeroes_and_ones_of_all_words[0]
            cnt = 1
            for index in lis:
                if index == 1:
                    files.append(files_with_index[cnt])
                cnt = cnt+1
            print(files)
except EOFError:
    pass

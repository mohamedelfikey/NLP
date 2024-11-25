# -*- coding: utf-8 -*-
"""1- IDMB using BOW.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15MG_ZVQG7OwH3bY5UhH8UzPuph9ff66V

# IMDB review sentiment analysis through text preprocessing and classification and build model

## Part one import basic libraries and read data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
import os

DATA_PATH=Path('./dat/')
DATA_PATH.mkdir(exist_ok=True)
#if not os.path.exists('./dat/aclImdb_v1.tar.gz'):
if not os.path.exists('./dat/aclImdb'):
    !curl -O http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz
    !tar -xf aclImdb_v1.tar.gz -C {DATA_PATH}

"""#### read data"""

import numpy as np
CLASSES = ['neg', 'pos']#, 'unsup']
PATH=Path('./dat/aclImdb/')

def get_texts(path):
    texts,labels = [],[]
    for idx,label in enumerate(CLASSES):
        for fname in (path/label).glob('*.*'):
            #texts.append(fixup(fname.open('r', encoding='utf-8').read()))
            texts.append(fname.open('r', encoding='utf-8').read())
            labels.append(idx)
    #return np.array(texts),np.array(labels)
    return texts, labels

trn_texts,trn_labels=get_texts(PATH/'train')
tst_texts,tst_labels=get_texts(PATH/'test')

for t in trn_texts[:10]:
  print (t,"\n")

"""## Part two data preprocessing and build vocab"""

def remove_special_chars(text):
    re1 = re.compile(r'  +')
    x1 = text.lower().replace('#39;', "'").replace('amp;', '&').replace('#146;', "'").replace(
        'nbsp;', ' ').replace('#36;', '$').replace('\\n', "\n").replace('quot;', "'").replace(
        '<br />', "\n").replace('\\"', '"').replace('<unk>', 'u_n').replace(' @.@ ', '.').replace(
        ' @-@ ', '-').replace('\\', ' \\ ')
    return re1.sub(' ', html.unescape(x1))



def remove_non_ascii(text):
    """Remove non-ASCII characters from list of tokenized words"""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')


def remove_punctuation(text):
    """Remove punctuation from list of tokenized words"""
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)


def to_lowercase(text):
    return text.lower()


def replace_numbers(text):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    return re.sub(r'\d+', '', text)

def remove_whitespaces(text):
    return text.strip()


def remove_stopwords(words, stop_words):
    """
    :param words:
    :type words:
    :param stop_words: from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
    or
    from spacy.lang.en.stop_words import STOP_WORDS
    :type stop_words:
    :return:
    :rtype:
    """
    return [word for word in words if word not in stop_words]


def stem_words(words):
    """Stem words in text"""
    stemmer = PorterStemmer()
    return [stemmer.stem(word) for word in words]

def lemmatize_words(words):
    """Lemmatize words in text"""

    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(word) for word in words]

def lemmatize_verbs(words):
    """Lemmatize verbs in text"""

    lemmatizer = WordNetLemmatizer()
    return ' '.join([lemmatizer.lemmatize(word, pos='v') for word in words])

def text2words(text):
  text=sent_tokenize(text)
  return word_tokenize("".join(text))

# clean scrapping
import html
import unicodedata
import string

# regex
import re

# tokenization
import nltk
nltk.download('punkt')

## sent_tokenize
from nltk.tokenize import sent_tokenize
## word_tokenize
from nltk.tokenize import word_tokenize

# remove stop words
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words=stopwords.words('english')

# stemming
from nltk.stem import PorterStemmer

# lemmatization
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
nltk.download('omw-1.4')


def normalize_text( text):
    text = remove_special_chars(text)
    text = remove_non_ascii(text)
    text = remove_punctuation(text)
    text = to_lowercase(text)
    text = replace_numbers(text)
    words = text2words(text)
    words = remove_stopwords(words, stop_words)
    #words = stem_words(words)# Either stem ovocar lemmatize

    #lemmatization is good in BOW
    words = lemmatize_words(words)
    words = lemmatize_verbs(words)

    return ''.join(words)

normalize_text(trn_texts[0])

def normalize_corpus (corpus):
  return [normalize_text(s) for s in corpus]

trn_texts=normalize_corpus(trn_texts)
tst_texts=normalize_corpus(tst_texts)

"""#### build vocab using keras Tokenizer with mode freq"""

# fit the tokenizer

from keras.preprocessing.text import Tokenizer
vocab_sz=10000
tok=Tokenizer(num_words=vocab_sz,oov_token="UNK")
tok.fit_on_texts(trn_texts+tst_texts)

tok.word_index

x_train=tok.texts_to_matrix(trn_texts,mode='freq')
x_test=tok.texts_to_matrix(tst_texts,mode='freq')

y_train=np.asarray(trn_labels).astype('float32')
y_test=np.asarray(tst_labels).astype('float32')

print (x_train.shape)
print (y_train.shape)
print (x_test.shape)
print (y_test.shape)

"""## Part three build network"""

from keras.layers import Dense
from keras.models import Sequential

model=Sequential()
model.add(Dense(16,activation='relu',input_shape=(10000,)))
model.add(Dense(16,activation='relu'))
model.add(Dense(1,activation='sigmoid'))
model.summary()

from keras.losses import binary_crossentropy
from keras.optimizers import RMSprop
from keras.metrics import binary_accuracy

model.compile(optimizer=RMSprop(lr=0.01),loss=binary_crossentropy,metrics=[binary_accuracy])

# split data
from sklearn.model_selection import train_test_split

x_train,x_val,y_train,y_val=train_test_split(x_train,y_train,test_size=.4,random_state=42)

history=model.fit(x_train,y_train,validation_data=(x_val,y_val),batch_size=512,epochs=20)

"""#### Evaluate the model"""

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend(['loss','val_loss'])
plt.title("BOW loss VS val_loss",fontweight="bold")
plt.show()

from sklearn.metrics import accuracy_score

# Make predictions on test data
predictions = model.predict(x_train)

# Since the predictions are probabilities, we need to convert them to binary values
# You can use a threshold of 0.5 for binary classification
binary_predictions = (predictions > 0.5).astype(int)

# Calculate accuracy
accuracy = accuracy_score(y_train, binary_predictions)

print("Accuracy on train data:", accuracy)

# Make predictions on test data
predictions = model.predict(x_test)

# Since the predictions are probabilities, we need to convert them to binary values
# You can use a threshold of 0.5 for binary classification
binary_predictions = (predictions > 0.5).astype(int)

# Calculate accuracy
accuracy = accuracy_score(y_test, binary_predictions)

print("Accuracy on test data:", accuracy)

# Use the trained model to predict labels for the test data
predictions = model.predict(x_val)

# Convert predicted probabilities to binary labels (0 or 1)
predicted_labels = (predictions > 0.5).astype(int)

# Calculate accuracy
accuracy = accuracy_score(y_val,predicted_labels)

print("Accuracy on test set:", accuracy)

"""### Show some predications of the model"""

review=[]
review.append(tst_texts[0])
review.append(tst_texts[1])
review.append(tst_texts[2])
review.append(tst_texts[3])
review.append(tst_texts[-1])
review.append(tst_texts[-2])
review.append(tst_texts[-3])
review.append(tst_texts[-4])

review_lbls=[]
review_lbls.append(tst_labels[0])
review_lbls.append(tst_labels[1])
review_lbls.append(tst_labels[2])
review_lbls.append(tst_labels[3])
review_lbls.append(tst_labels[-1])
review_lbls.append(tst_labels[-2])
review_lbls.append(tst_labels[-3])
review_lbls.append(tst_labels[-4])

text=[]
text.append(x_test[0])
text.append(x_test[1])
text.append(x_test[2])
text.append(x_test[3])
text.append(x_test[-1])
text.append(x_test[-2])
text.append(x_test[-3])
text.append(x_test[-4])
text=np.array(text)
text

labels=[]
labels.append(tst_labels[0])
labels.append(tst_labels[1])
labels.append(tst_labels[2])
labels.append(tst_labels[3])
labels.append(tst_labels[-1])
labels.append(tst_labels[-2])
labels.append(tst_labels[-3])
labels.append(tst_labels[-4])

# Make predictions on test data
predictions = model.predict(text)

# Since the predictions are probabilities, we need to convert them to binary values
# You can use a threshold of 0.5 for binary classification
binary_predictions = (predictions > 0.5).astype(int)

df=pd.DataFrame({'review':review,'labels':review_lbls,'pred_labels':list(binary_predictions)})
df['pred_labels'] = df['pred_labels'].apply(lambda x: x[0])
df

"""__Even if the accuracy achieved using the bag-of-words approach may not be as high as desired but it's satisfied, there are still several advantages to using this method for text classification, the most important thing is speed and feed data to neural networl__"""
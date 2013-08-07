from __future__ import division
from dateutil.parser import parse
from nltk.tokenize import WordPunctTokenizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import time
import datetime

## SETTING PARAMETERS
use_stop_words = False
min_word_len = 3
snapshot_date = datetime.datetime(2013,3,13)

## REVIEW DATA
print "loading review data from csv file..."
review = pd.read_csv('Data\\yelp_test_set_review.csv',
                     converters={'date': parse}).set_index('review_id')
review = review.drop(['type'],axis=1)
review['text'] = review['text'].fillna("")
review['review_len'] = review['text'].apply(len) 
 
tokenizer = WordPunctTokenizer()
stemmer = PorterStemmer()
if use_stop_words:
    stopset = set(stopwords.words('english'))
    print "using stop words"
else:
    stopset = []
    print "stemming all words - stop words discarded"
 

print "stemming words - min word length is: "+str(min_word_len)
stemmedReview = []
init_time = time.time()
for i in range(len(review)):
    stemmedReview.append(
        [stemmer.stem(word) for word in [w for w in # stem the word
            tokenizer.tokenize(review.ix[i,'text'].lower()) # tokenize with punct the lower cased review
                if (len(w) > min_word_len and w not in stopset)] # exclude stopword and shorter than 3
        ] # put everything in a list
    )
 
print (time.time()-init_time)/60

review['text'] = stemmedReview
del stemmedReview
review['stem_len'] = review['text'].apply(len)
review['stem_unique_len'] = review['text'].apply(np.unique).apply(len)
review['text'] = [' '.join(words) for words in review['text']]

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import joblib
vect = joblib.load('Models\\review_vect')
print "extracting feature"
stem_fea = vect.transform(review['text']).todense()

#SCALE FEATURE to adjust importance for KMEAN
steam_fea = np.log((stem_fea/0.5)+1)

from sklearn.cluster import MiniBatchKMeans
for esti in (200,300,500,750,1000):
    print "setting nearest cluster - # clusters: "+str(esti)
    km = joblib.load('Models\\review_km'+str(esti))
    review['clust_'+str(esti)] = km.predict(stem_fea)
    

review['stem_unique_len_ratio'] = review['stem_unique_len'] / review['stem_len']
review['date'] = snapshot_date - review['date']
review['date'] = review['date'].apply(lambda d: d.days)

review.to_csv('DataProcessed\\review_test_fea.csv')



    

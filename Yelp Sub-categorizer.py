__author__ = 'Steve_Jobs'
import os
import json
import string
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
data_dir='/Users/Steve_Jobs/Desktop/yelp_dataset_challenge_academic_dataset'
Business_Filename='yelp_academic_dataset_business.json'
Reviews_Filename='yelp_academic_dataset_review.json'
Typestoconsider=['Restaurants','Bars', 'Wine Bars','Coffee & Tea','Fast Food','Seafood','Indian','Food', 'Donuts','Steakhouses','Ice Cream & Frozen Yogurt','Pizza', 'Salad','Delis', 'Sandwiches']
datatoremovefromreview=['business_id','text','review_id','type','date','user_id']
businessesdata={}
reviewsdata={}
reviewtokenizer = RegexpTokenizer(r'[a-zA-Z]+')

def read_businesses(filepath):
    with open(filepath) as jsonfile:
        for eachline in jsonfile:
            eachbusiness= json.loads(eachline)
            for eachcat in eachbusiness['categories']:
                if(Typestoconsider.__contains__(eachcat)):
                    businessesdata[eachbusiness['business_id']]=dict(eachbusiness)
                    break
def textpreprocess(reviewtext,wordsdict):
    stopwordslist=stopwords.words('english')
    stopwordslist.sort()
    reviewtext=reviewtext.lower()
    reviewtokens=reviewtokenizer.tokenize(reviewtext)
    reviewtokens.sort()
    for eachtoken in reviewtokens:
        if not stopwordslist.__contains__(eachtoken):
            try:
                wordsdict[eachtoken]=wordsdict[eachtoken]+1
            except:
                wordsdict[eachtoken]=1
    return wordsdict



def read_reviews(reviewsfile):
    with open(reviewsfile) as jsonfile:
        i=0
        for eachline in jsonfile:
            i=i+1
            print(i)
            review= json.loads(eachline)
            if(businessesdata.__contains__(review['business_id'])):
                businessid=review['business_id']
                reviewtext=review['text']
                try:
                    eachbusinessreviews=reviewsdata[businessid]
                    reviewwordsdict=eachbusinessreviews['review']
                    # businessreview=businessreview+review['text']
                    allreviewswordsdict=textpreprocess(reviewtext,reviewwordsdict)
                    for eachitem in datatoremovefromreview:
                        review.pop(eachitem)
                    noofreviews=eachbusinessreviews.__len__()
                    eachbusinessreviews[noofreviews]=review
                    eachbusinessreviews['review']=dict(allreviewswordsdict)
                    reviewsdata[businessid]=eachbusinessreviews
                except:
                    wordsdict={}
                    wordsdict=textpreprocess(reviewtext,wordsdict)
                    for eachitem in datatoremovefromreview:
                        review.pop(eachitem)
                    eachbusinessreviews={1:review}
                    eachbusinessreviews['review']=wordsdict
                    reviewsdata[businessid]=eachbusinessreviews
    print(reviewsdata)


def main():
    read_businesses(os.path.join(data_dir,Business_Filename))
    read_reviews(os.path.join(data_dir,Reviews_Filename))

main()

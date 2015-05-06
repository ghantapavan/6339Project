__author__ = 'Steve_Jobs'
import os
import json
import string
import math
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from collections import OrderedDict
import time
import csv
import json
# Dictionary to store the subtopics and their respective best restaurants
finalresults={}
data_dir=os.path.curdir
#File containing business data
Business_Filename='yelp_academic_dataset_business.json'

#File containing reviews data
Reviews_Filename='yelp_academic_dataset_review.json'

#file to store the pre-calculated results
resultsfile="results.json"

#Types of businesses considered for review
Typestoconsider=['Restaurants','Bars', 'Wine Bars','Coffee & Tea','Fast Food','Seafood','Indian','Food', 'Donuts','Steakhouses','Ice Cream & Frozen Yogurt','Pizza', 'Salad','Delis', 'Sandwiches']
datatoremovefromreview=['business_id','text','review_id','type','date','user_id']
#Dictionary to manage the subtopic and its summary
SUBTOPICSUMMARY={'Good for Work':['calm','work','wifi','wi-fi','cofee','tea','spacious'],'Good for Game day':['tv','nfl','sports','football','soccer','basketball','game'],'Less waiting time':['less','waiting','time','good','quick','fast','parking','drive'],'Good for group hangout':['friends','groups','group','hang-out','hangout','meet','hang','discuss','sit','talk']}
GOODCONTEXT=['good','great','fantastic','amazing','nice','better','best','like']
BADCONTEXT=['bad','rude','worst']
Context={}
businessesdata={}
reviewsdata={}
reviewtokenizer = RegexpTokenizer(r'[a-zA-Z]+')
stemmer = PorterStemmer()
allWordsCount={}
NoofReviews=1

#method to read the business data from businesses json file
def read_businesses(filepath):
    with open(filepath) as jsonfile:
        for eachline in jsonfile:
            eachbusiness= json.loads(eachline)
            for eachcat in eachbusiness['categories']:
                if(Typestoconsider.__contains__(eachcat)):
                    businessesdata[eachbusiness['business_id']]=dict(eachbusiness)
                    break

#method to remove stopwords and calculate word frequency in the review and all reviews
def textpreprocess(reviewtext,wordsdict):
    stopwordslist=stopwords.words('english')
    stopwordslist.sort()
    reviewtext=reviewtext.lower()
    reviewtokens=reviewtokenizer.tokenize(reviewtext)
    reviewtokens.sort()
    reviewcompletetext=[]
    tmpflag=True
    tmpwordsdict={}
    for eachtoken in reviewtokens:
        if not stopwordslist.__contains__(eachtoken):
            reviewcompletetext.append(eachtoken)
            if not tmpwordsdict.__contains__(eachtoken):
                try:
                    allWordsCount[eachtoken]=allWordsCount[eachtoken]+1
                except:
                    allWordsCount[eachtoken]=1
                tmpwordsdict[eachtoken]=1

            try:
                wordsdict[eachtoken]=wordsdict[eachtoken]+1
            except:
                wordsdict[eachtoken]=1
    return wordsdict

#method to calculate tfidf values of a business review(combined review for a business)
def calctfidf(reviewwordsdict):
    reviewtfidfdict={}
    worddocscount=1
    for eachkey in reviewwordsdict:
        tf=reviewwordsdict[eachkey]
        wt=0.0
        try:
            worddocscount=allWordsCount[eachkey]
        except:
            pass
        wt=(1+math.log10(tf))*math.log10(NoofReviews/worddocscount)
        reviewtfidfdict[eachkey]=wt
    sumofsquare=0
    for eachvalue in reviewtfidfdict.values():
        sumofsquare=sumofsquare+eachvalue*eachvalue
    sumofsquare=math.sqrt(sumofsquare)
    for eachkey in reviewtfidfdict.keys():
        eachidfvalue=reviewtfidfdict[eachkey]
        eachidfvalue=eachidfvalue/sumofsquare
        reviewtfidfdict[eachkey]=eachidfvalue
    return reviewtfidfdict

#Read reviews from reviews file
def read_reviews(reviewsfile):
    with open(reviewsfile) as jsonfile:
        i=0
        for eachline in jsonfile:
            i=i+1
            review= json.loads(eachline)
            if(businessesdata.__contains__(review['business_id'])):
                businessid=review['business_id']
                reviewtext=review['text']

                try:
                    eachbusinessreviews=reviewsdata[businessid]
                    reviewwordsdict=eachbusinessreviews['review']
                    allreviewswordsdict=textpreprocess(reviewtext,reviewwordsdict)
                    for eachitem in datatoremovefromreview:
                        review.pop(eachitem)
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
    return

def allreviewstfidf():

    for businessid in reviewsdata.keys():
        allreviewswordsdict={}
        eachbusinessreviews1=dict(reviewsdata[businessid])
        allreviewswordsdict=eachbusinessreviews1['review']
        eachbusinessreviews1['tfidf']=dict(calctfidf(allreviewswordsdict))
        reviewsdata[businessid]=eachbusinessreviews1
    return

#method to calculate tfidf values of a sub-topic
def querytfidf(listofwords):
    wordcountindoc=0
    tfidfdict={}
    for eachword in listofwords:
        try:
            tfidfdict[eachword]=tfidfdict[eachword]+1
        except:
            tfidfdict[eachword]=1
    return calctfidf(tfidfdict)

#Reads the pre-calculated results for sub-topics
def readresults():
    with open(os.path.join(data_dir,resultsfile)) as resultfile:
        for eachline in resultfile:
            eachtopicdata= json.loads(eachline)
            for k,v in eachtopicdata.items():
                # print(k)
                finalresults[k]=v
            
    
#Displays the options,which drives the program execution.Select a sub-topic to display the best restaurants
#Select 99 to re-process the reviews.(It may take 25-35 minutes)
def display():
    tmpflag=True
    displaydict=OrderedDict()
    k=1
    read_businesses(os.path.join(data_dir,Business_Filename))
    NoofReviews=businessesdata.__len__()
    for eachtopickey in SUBTOPICSUMMARY.keys():
        displaydict[int(k)]=eachtopickey
        k=k+1
    while(True):
        print('List of sub-topics:')
        for eachitem in displaydict.items():
            print(eachitem.__getitem__(0),'.',eachitem.__getitem__(1))
        print('99','.','Full Calculate')
        print('100','.','Exit')
        print('Enter a number to display results for the subtopic:(e.g.,1)')
        choice=input("Enter your choice:")
        if(choice=='99'):
            main()
        elif(choice=='100'):
            break
        else:
            if(tmpflag):
                readresults()
                tmpflag=False
            print("Displaying top restaurants for the sub-category:",displaydict[int(choice)])
            businessname=""
            for eachbussinessid in finalresults[displaydict[int(choice)]]:
                businessname=businessesdata[eachbussinessid]['name']
                print(eachbussinessid,":",businessname)
            input('Press Enter to continue')
    

#Calculates cosine similarity between each subtopic and all the business reviews.
#Select the top 100 restaurants(high cosine values) for a subtopic and stores in a dictionary.Also
#writes the results to results file
def main():
    Results={}
    read_reviews(os.path.join(data_dir,Reviews_Filename))
    allreviewstfidf()
    for eachbussid in reviewsdata.keys():
        try:
            reviewtfidf=reviewsdata[eachbussid]['tfidf']
        except:
            pass
        
        # tmpcontextdict={}
        # goodvalue=0
        #
        # for eachword in GOODCONTEXT:
        #     try:
        #         goodvalue=goodvalue+reviewtfidf[eachword]
        #     except:
        #         pass
        # tmpcontextdict['good']=goodvalue
        # badvalue=0
        # for eachword in BADCONTEXT:
        #     try:
        #         badvalue=badvalue+reviewtfidf[eachword]
        #     except:
        #         pass
        # tmpcontextdict['bad']=badvalue
        # Context[eachbussid]=tmpcontextdict

        for eachtopic in SUBTOPICSUMMARY.keys():
            try:
                tmpsimvalues=Results[eachtopic]
            except:
                tmpsimvalues={}
            eachitemkeywords=SUBTOPICSUMMARY[eachtopic]
            querytfidfvals=querytfidf(eachitemkeywords)
            reviewvalue=0
            for eachsummword in eachitemkeywords:
                try:
                    wordtfidf=reviewtfidf[eachsummword]
                except:
                    wordtfidf=0
                reviewvalue=reviewvalue+wordtfidf*querytfidfvals[eachsummword]
            tmpsimvalues[eachbussid]=reviewvalue
            Results[eachtopic]=dict(tmpsimvalues)
        
    for eachsubtopic in SUBTOPICSUMMARY.keys():
        busslist=[]
        cosval=[]
        eachtopicresults=[]
        for key, value in sorted(Results[eachsubtopic].items(), key=lambda item: (item[1],item[0])):
            busslist.append(key)
            cosval.append(value)
        l=-1
        for val in reversed(cosval):
            if(l>-100):
                busskey=busslist[l]
                eachtopicresults.append(busskey)
                l=l-1
        finalresults[eachsubtopic]=eachtopicresults
    resultsfilewrite=open(os.path.join(data_dir,resultsfile), 'w')
    json.dump(finalresults, resultsfilewrite)

display()
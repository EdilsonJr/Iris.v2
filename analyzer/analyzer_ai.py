import pandas as pd
import warnings

warnings.filterwarnings('ignore')
from sklearn.naive_bayes import MultinomialNB
from sklearn.multiclass import OneVsRestClassifier
from sklearn import metrics
from sklearn.metrics import accuracy_score
from pandas.plotting import scatter_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics

import re

from wordcloud import WordCloud

from sklearn.preprocessing import LabelEncoder

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack

from django.db import connection, connections
from django.conf import settings

import pickle

print("Importing the dataset...")
resumeDataSet = pd.read_csv('training_dataset/Resume_Data.csv', error_bad_lines=False)
resumeDataSet['cleaned_resume'] = ''

print("Cleaning text data...")


def cleanResume(resumeText):
    resumeText = re.sub('http\S+\s*', ' ', resumeText)  # remove URLs
    resumeText = re.sub('RT|cc', ' ', resumeText)  # remove RT and cc
    resumeText = re.sub('#\S+', '', resumeText)  # remove hashtags
    resumeText = re.sub('@\S+', '  ', resumeText)  # remove mentions
    resumeText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ',
                        resumeText)  # remove punctuations
    resumeText = re.sub(r'[^\x00-\x7f]', r' ', resumeText)
    resumeText = re.sub('\s+', ' ', resumeText)  # remove extra whitespace
    return resumeText


resumeDataSet['cleaned_resume'] = resumeDataSet.Resume.apply(lambda x: cleanResume(x))

print("Vectorizing categories...")
categories = resumeDataSet['Category']
var_mod = ['Category']
le = LabelEncoder()
for i in var_mod:
    resumeDataSet[i] = le.fit_transform(resumeDataSet[i])

print("Separeting the categories...")
all_category_num = []
unique_category_num = []
for index in range(len(categories)):
    all_category_num.append('' + str(categories[index]) + ' - ' + str(resumeDataSet['Category'].iloc[index]))

for item in all_category_num:
    if item not in unique_category_num:
        unique_category_num.append(item)

print("Vectorizing the text data...")
requiredText = resumeDataSet['cleaned_resume'].values
requiredTarget = resumeDataSet['Category'].values

word_vectorizer = TfidfVectorizer(
    sublinear_tf=True,
    stop_words='english',
    max_features=1500)
word_vectorizer.fit(requiredText)
WordFeatures = word_vectorizer.transform(requiredText)
print("Feature completed .....")

X_train, X_test, y_train, y_test = train_test_split(WordFeatures, requiredTarget, random_state=0, test_size=0.2)

print("Creating and fitting the AI model...")
clf = OneVsRestClassifier(KNeighborsClassifier())
clf.fit(X_train, y_train)
prediction = clf.predict(X_test)
print('Accuracy of KNeighbors Classifier on training set: {:.2f}'.format(clf.score(X_train, y_train)))
print('Accuracy of KNeighbors Classifier on test set: {:.2f}'.format(clf.score(X_test, y_test)))
print("\n Classification report for classifier %s:\n%s\n" % (clf, metrics.classification_report(y_test, prediction)))

print("Organizing the results...")
predictions_result = []
for index in range(len(prediction)):
    for category in unique_category_num:
        category = category.split('-')
        if int(category[1]) == int(prediction[index]):
            predictions_result.append(("Item - " + str(index), "Category - " + str(category[0])))

print("Saving the model to the DB...")
settings.configure(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'main_app',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3309',
    },
})
pickled_model = pickle.dumps(clf)
with connection.cursor() as cursor:
    try:
        sql = "REPLACE INTO analyzer (version, name, model) VALUES (%s, %s, %s);"
        cursor.execute(sql, (1, 'ResumeAnalyzer', pickled_model))
    except BaseException as err:
        print("An error occurred while saving the model in the db")
        print('ERROR: {}'.format(err))

print("DONE!")

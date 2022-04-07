from numpy import mean
import pickle
import string
import re
import pandas as pd

from django.db import connection
from django.conf import settings

from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, accuracy_score

from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score

from sklearn.preprocessing import LabelEncoder

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import nltk
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
except FileExistsError:
    pass

from imblearn.over_sampling import RandomOverSampler
# from collections import Counter

import warnings
warnings.filterwarnings("ignore")


def text_preprocessing(content):
    stop_words = set(stopwords.words("english"))
    
    # Making his content lower case
    content = content.lower()
     
    # Removing HTML Tags
    html_removal_code = re.compile('<.*?>') 
    content = re.sub(html_removal_code, '', content)

    # Removing ponctuation
    content = content.translate(str.maketrans("", "", string.punctuation))

    # Removing white spaces
    content = content.strip()

    # Removing stop words
    word_tokens = word_tokenize(content)
    # filtered_text = [word for word in word_tokens if word not in stop_words]
    filtered_text = ''
    for word in word_tokens:
        if word not in stop_words:
            filtered_text = filtered_text + word + " "
    content = filtered_text.strip()

    return content


def svm_create_model(X, y, data_split_type='holdout', to_pred=(False,)):
    svc = SVC(C=1, kernel='linear', gamma='auto', decision_function_shape='ovr', random_state=47, probability=True)
    
    if data_split_type == 'kfold':
        k_fold = KFold(n_splits=10, random_state=1, shuffle=True)
        kfold_scores = cross_val_score(svc, X, y, scoring='accuracy', cv=k_fold, n_jobs=6)
        k_fold_accuracy = mean(kfold_scores)
        print(f'Kfold Accuracy: {mean(kfold_scores)}')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=23)
    
    svc.fit(X_train, y_train)
    svc_pred = svc.predict(X_test)
    
    accuracy = accuracy_score(y_test, svc_pred)
    precision = precision_score(y_test, svc_pred, average='macro')
    recall = recall_score(y_test, svc_pred, average='macro')
    print("Precision = {}".format(precision))
    print("Recall = {}".format(recall))
    print("Accuracy = {}".format(accuracy))
    
    print(classification_report(y_test, svc_pred))
    return (svc, k_fold_accuracy, precision, recall)

def nb_create_model(X, y, data_split_type='holdout'):
    nb = MultinomialNB()
    
    if data_split_type == 'kfold':
        k_fold = KFold(n_splits=10, random_state=1, shuffle=True)
        kfold_scores = cross_val_score(nb, X, y, scoring='accuracy', cv=k_fold, n_jobs=6)
        k_fold_accuracy = mean(kfold_scores)
        print(f'Kfold Accuracy: {mean(kfold_scores)}')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=23)
    
    nb.fit(X, y)
    
    nb_pred = nb.predict(X_test)
    nb_pred_proba = nb.predict_proba(X_test)
    
    # accuracy = accuracy_score(y_test, nb_pred)
    # precision = precision_score(y_test, nb_pred, average='macro')
    # recall = recall_score(y_test, nb_pred, average='macro')
    # print(f"Accuracy = {accuracy}")
    # print(f"Precision = {precision}")
    # print(f"Recall = {recall}")
    
    # print(f"Predict Proba = {nb_pred_proba[0]}")
    
    print(classification_report(y_test, nb_pred))
    precision, recall = 0, 0
    return (nb, k_fold_accuracy, precision, recall)


resumes = pd.read_csv('training_dataset/Resume_Data.csv')


resumes['cleaned_resume'] = ''
for i in range(len(resumes['Resume'])):
    resume = resumes['Resume'].iloc[i]
    resumes['cleaned_resume'].iloc[i] = text_preprocessing(resume)


le = LabelEncoder()
resumes['encoded_label'] = le.fit_transform(resumes['Category'])


X = resumes['cleaned_resume']
y = resumes['encoded_label']


word_vectorizer = TfidfVectorizer(
    sublinear_tf=True,
    strip_accents='unicode',
    analyzer='word',
    token_pattern=r'\w{1,}',
    ngram_range=(1, 1),
    norm='l2',
    min_df=0,
    smooth_idf=False,
    max_features=15000)

# Vectorize X
word_vectorizer.fit(X) 
train_word_features = word_vectorizer.transform(X)


over_sampler = RandomOverSampler(random_state=42)
X_res, y_res = over_sampler.fit_resample(train_word_features, y)


# svc_model, accuracy, precision, recall = svm_create_model(X_res, y_res, data_split_type='kfold') # SVC
nb_model, accuracy, precision, recall = nb_create_model(X_res, y_res, data_split_type='kfold') # NaiveBayes


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

pickled_model = pickle.dumps(nb_model)
pickled_word_vec = pickle.dumps(word_vectorizer)
pickled_le = pickle.dumps(le)

print(f'pickled_model: {type(str(pickled_model))}')

with connection.cursor() as cursor:
    try:
        # sql = """REPLACE INTO analyzer (version, name, model, word_vec, label_encoder, status, `precision`, recall, accuracy) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        # cursor.execute(sql % (2, 'ResumeAnalyzer', pickled_model, pickled_word_vec, pickled_le, 'OK', float(precision), float(recall), float(accuracy)))
        
        sql = "REPLACE INTO analyzer (version, name, model, word_vec, label_encoder, status, recall, accuracy) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        print(sql)
        cursor.execute(sql, (2, 'ResumeAnalyzerNB', pickled_model, pickled_word_vec, pickled_le, 'OK', recall, accuracy))
    except BaseException as err:
        print("An error occurred while saving the model in the db")
        print('ERROR: {}'.format(err))

print("DONE!")
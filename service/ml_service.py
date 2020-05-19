import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.neighbors import KNeighborsClassifier
import nltk
import app


nltk.download('stopwords')


def ml(filename):
    data = pd.read_csv(app.UPLOAD_FOLDER + filename)
    df = pd.DataFrame(data, columns=['review'], dtype=str)
    path = pd.read_csv(r'processed_youtubeMusic_labelled.csv')
    df_train = pd.DataFrame(path, columns=['review'], dtype=str)

    # trainign model
    train_sentences = []
    for i, row in df_train.iterrows():
        train_sentences.append(df_train['review'].loc[i])

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(train_sentences)

    y_train = np.zeros(257)
    y_train[0:88] = 0
    y_train[89:143] = 1
    y_train[144:199] = 2
    y_train[200:257] = 3

    modelknn = KNeighborsClassifier(n_neighbors=5)
    modelknn.fit(X, y_train)
    # output
    test_sentences = []
    for i, row in df.iterrows():
        test_sentences.append(df['review'].loc[i])

    Test = vectorizer.transform(test_sentences)

    true_test_labels = ['Strength', 'Opportunity', 'Weakness', 'Threat']
    predicted_labels_knn = modelknn.predict(Test)

    z = []
    for i, row in df.iterrows():
        z.append((true_test_labels[np.int(predicted_labels_knn[i])]))
    # writting results to a casv
    df['classified'] = z
    #df.to_csv(app.RESULTS_FOLDER,filename + "results.csv")
    df.to_csv(os.path.join(app.RESULTS_FOLDER, filename+'_results.csv'))

    # returning values
    def str_string(classified_reviews):
        if 'Strength' in classified_reviews:
            return True
        else:
            return False

    def opp_string(classified_reviews):
        if 'Opportunity' in classified_reviews:
            return True
        else:
            return False

    def weak_string(classified_reviews):
        if 'Weakness' in classified_reviews:
            return True
        else:
            return False

    def threat_string(classified_reviews):
        if 'Threat' in classified_reviews:
            return True
        else:
            return False

    # print("check results.csv for clusters")
    print(df['classified'].value_counts())
    strenths = sum(df['classified'].apply(lambda x: str_string(x)))
    opportunities = sum(df['classified'].apply(lambda y: opp_string(y)))
    weaknessess = sum(df['classified'].apply(lambda w: weak_string(w)))
    threats = sum(df['classified'].apply(lambda t: threat_string(t)))
    total = len(df.index)
    #print(strenths,weaknessess,threats,opportunities,total)
    return strenths, opportunities, weaknessess, threats, total


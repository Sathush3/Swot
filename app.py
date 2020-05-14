import os
from flask import Flask, render_template, flash, jsonify
from flask import redirect, url_for
from flask import request
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.neighbors import KNeighborsClassifier
import nltk
nltk.download('stopwords')

app = Flask(__name__)
UPLOAD_FOLDER = 'G:\FYP'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def hello_world():
    return 'success'


@app.route('/user/<user_login>/')
def test(user_login):
    if user_login == 'login':
        return redirect(url_for('login'))
    elif user_login == 'signup':
        return redirect(url_for('signup'))
    elif user_login == 'forgot':
        return redirect(url_for('forgot'))


@app.route('/user/login/', methods=['POST'])
def login():
    email_login = None
    password_login = None
    req_data = request.get_json()
    if 'email' in req_data:
        email_login = req_data['email']
    if 'password' in req_data:
        password_login = req_data['password']
    return render_template('login.html', email=email_login, password=password_login)


@app.route('/user/signup/', methods=['POST'])
def signup():
    email_signup = None
    name_signup = None
    password_signup = None
    req_data_1 = request.get_json()
    if 'email' in req_data_1:
        email_signup = req_data_1['email']
    if 'name' in req_data_1:
        name_signup = req_data_1['name']
    if 'password' in req_data_1:
        password_signup = req_data_1['password']

    return render_template('signup.html', name=name_signup, email=email_signup, password=password_signup)


@app.route('/user/forgot/')
def forgot():
    mail = request.args.get('email')
    return 'the email is :{}'.format(mail)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file',
                                    filename=filename))


@app.route('/upload/test/', methods=['POST'])
def upload_test():
    file = request.files['file']
    data = pd.read_csv(file)
    df = pd.DataFrame(data, columns=['review'], dtype=str)

    path = pd.read_csv(r'processed_youtubeMusic_labelled.csv')
    df_train = pd.DataFrame(path, columns=['review'], dtype=str)

    # stop = set(stopwords.words('english'))
    # exclude = set(string.punctuation)
    # lemma = WordNetLemmatizer()

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

    test_sentences = []
    for i, row in df.iterrows():
        test_sentences.append(df['review'].loc[i])

    Test = vectorizer.transform(test_sentences)

    true_test_labels = ['Strength', 'Opportunity', 'Weakness', 'Threat']
    predicted_labels_knn = modelknn.predict(Test)

    z = []
    for i, row in df.iterrows():
        z.append((true_test_labels[np.int(predicted_labels_knn[i])]))

    df['classified'] = z
    df.to_csv("results.csv")

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

    print("check results.csv for clusters")
    print(df['classified'].value_counts())
    strenths = sum(df['classified'].apply(lambda x: str_string(x)))
    opportunities = sum(df['classified'].apply(lambda y: opp_string(y)))
    weaknessess = sum(df['classified'].apply(lambda w: weak_string(w)))
    threats = sum(df['classified'].apply(lambda t: threat_string(t)))
    total = len(df.index)
    a = '''The strength are {}
    The opportunities are {}
    The weakness are {}
    The Threats are{}
    total is {}'''.format(strenths, opportunities, weaknessess, threats, total)

    return jsonify(
        strength=strenths,
        opportunity=opportunities,
        weaknes=weaknessess,
        threat=threats,
        totals=total
    )


if __name__ == '__main__':

    app.run()

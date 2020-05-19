from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail

import service.user_service as userService
from service import ml_service, upload_service
from service.mail_service import MailService

mail = Mail()

app = Flask(__name__)
cors = CORS(app)
UPLOAD_FOLDER = './inputs/'
RESULTS_FOLDER = './results/'
FOLDER = 'results/'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["CLIENT_CSV"] = RESULTS_FOLDER

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_USERNAME'] = 'help.musican@gmail.com'
app.config['MAIL_PASSWORD'] = 'Qwerty@12345'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'help.musican@gmail.com'
mail.init_app(app)


@app.route('/')
def hello():
    return "Music Annalyzer is up and running"


@app.route('/user/signup', methods=['POST'])
def userSignUp():
    respsone = {}

    try:
        email = request.json['email']
        name = request.json['name']
        password = request.json['password']

        if (email == None or not email):
            raise Exception('email is required')

        if (name == None or not name):
            raise Exception('name is required')

        if (password == None or not password):
            raise Exception('password is required')

        if (not userService.findUserIDByEmail(email) == None):
            raise Exception("User with email already exist")

        userId = userService.createUserAccount(name, email, password)

        MailService.sendVerificationEmail(mail, email, userId)

        if (userId):
            respsone = {
                'object': str(userId),
                'status': "OK",
                'message': "Successfuly created user"
            }
        else:
            raise Exception("Error occured when creating an user")

    except Exception as e:
        print(e)
        respsone = {
            'object': None,
            'status': "ERROR",
            'message': str(e)
        }

    return jsonify(respsone), 400 if respsone['status'] == "ERROR" else 200


@app.route('/user/login', methods=['POST'])
def userLogIn():
    respsone = {}

    try:
        email = request.json['email']
        pswd = request.json['password']

        if (not email):
            raise Exception("Email field cannot be empty")
        if (not pswd):
            raise Exception("Password field cannot be empty")

        user = userService.findUserByEmail(email)

        if not user['password'] == pswd:
            raise Exception("Password is not valid")

        if not user['verified']:
            MailService.sendVerificationEmail(mail, email, user['_id'])
            raise Exception('Account not verfied, Please check inbox')

        userService.logInUser(str(user['_id']))

        respsone = {
            'object': str(user['_id']),
            'status': "OK",
            'message': "User successfully logged in"
        }

    except Exception as e:

        respsone = {
            'object': None,
            'status': "ERROR",
            'message': str(e)
        }

    return jsonify(respsone), 400 if respsone['status'] == "ERROR" else 200


@app.route('/user/logout/<id>')
def userLogOut(id):
    try:
        userService.logOutUser(id)
        respsone = {
            'object': None,
            'status': "OK",
            'message': "User successfully logged out"
        }

    except Exception as e:
        respsone = {
            'object': None,
            'status': "ERROR",
            'message': str(e)
        }

    return jsonify(respsone), 400 if respsone['status'] == "ERROR" else 200


@app.route('/user/forgot/')
def userForgot():
    respsone = None
    try:

        email = request.args.get('email')

        if not email:
            raise Exception("Invalid Email")

        userId = userService.findUserIDByEmail(email)

        if (userId == None):
            raise Exception("User doesn't exist")

        MailService.sendUserResetEmail(mail, email, userId)

        respsone = {
            'object': None,
            'status': "OK",
            'message': "Reset Email Sent, Check Inbox or Spam"
        }

    except Exception as e:
        print(e)
        respsone = {
            'object': None,
            'status': "ERROR",
            'message': str(e)
        }

    return jsonify(respsone), 400 if respsone['status'] == "ERROR" else 200


@app.route('/user/reset/<id>', methods=['POST'])
def userReset(id):
    response = None
    try:
        newPass = request.form['new_pass']
        conPass = request.form['con_pass']
        print('new pass', newPass)
        print('con pass', conPass)

        if (conPass != newPass):
            raise Exception("Passwords entered do not match, Try again")
        elif not id:
            raise Exception("Error occured when resetting password for user, Try again")

        userService.resetPassword(id, newPass)
        response = "Successfuly Changed User Password"

    except Exception as e:
        response = str(e)

    return response


@app.route('/user/verify/<id>')
def userVerify(id):
    response = "None"
    try:
        if (not id):
            raise Exception('Error occured in verifying user')
        userService.verifyUserAccount(id)
        response = "Email Successfully Verified"
    except Exception as e:
        print("Exception occured", e)
        response = "Error Occured when verfiying User. Try again later!"

    return response


@app.route('/user/status/<id>')
def userStatus(id):
    response = {}

    try:
        user = userService.findUserByID(id)

        if (user['active']):

            respsone = {
                'object': str(user['_id']),
                'status': "OK",
                'message': "User is active"
            }
        else:
            raise Exception("User not active")

    except Exception as e:

        respsone = {
            'object': None,
            'status': "ERROR",
            'message': str(e)
        }

    return jsonify(respsone), 400 if respsone['status'] == "ERROR" else 200


@app.route('/upload/<id>/', methods=['POST'])
def upload_test(id):
    response = {}
    try:
        user = userService.findUserByID(id)

        if (user['active']):
            if request.method == 'POST':
                file = request.files['file']
                filename = upload_service.file_save(file, id)
                strenths, opportunities, weaknessess, threats,positives,negatives, total = ml_service.ml(filename)
                # print(output)
                response = {
                    'Strength': strenths,
                    'Opportunity': opportunities,
                    'Weakness': weaknessess,
                    'Threats': threats,
                    'Positives':positives,
                    'Negatives':negatives,
                    'Total': total
                }

        else:
           raise Exception("User not active")
    except Exception as e:

        response = {
            'object': None,
            'status': "ERROR",
            'message': str(e)
        }

    return jsonify(response)


if __name__ == '__main__':
    app.run()

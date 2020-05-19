from database.database import Database
from service.mail_service import MailService
from model.User import User
from flask_mail import Message
from bson.objectid import ObjectId

db = Database()

userCollection = db.getCollection('user')

def createUserAccount(name, email, password):

    userModel = User(name, email, password)
    _id = userCollection.insert(userModel.__dict__)
    return _id

def findUserIDByEmail(email):

    user = userCollection.find_one({"email":email})
    userId = None
    if(user):
        userId = str(user['_id'])

    return userId

def findUserByEmail(email):

    user = userCollection.find_one({"email":email})
    print("User is there")
    if(not user):
        raise Exception("User account not found")
    return user

def findUserByID(id):

    user = userCollection.find_one({"_id":ObjectId(id)})
    
    if(not user):
        raise Exception("User account not found")
    return user

def verifyUserAccount(id):
    
     updatedUser = userCollection.update({"_id": ObjectId(id) }, {"$set": { "verified": True }})
     print("This is the updated users id", updatedUser)

     if(updatedUser == None or not updatedUser['updatedExisting']):
         raise Exception("Error occured during verification Proccess, Please try again")


def resetPassword(id, password):
    
     updatedUser = userCollection.update({"_id": ObjectId(id) }, {"$set": { "password": password, "active": False}})
     print("This is the updated users id", updatedUser)

     if(updatedUser == None or not updatedUser['updatedExisting']):
         raise Exception("Error occured during the password reset proccess, Please try again")

def logInUser(id):

     updatedUser = userCollection.update({"_id": ObjectId(id) }, {"$set": { "active": True}})
     print("This is the updated users id", updatedUser)

     if(updatedUser == None or not updatedUser['updatedExisting']):
         raise Exception("Error occured during user login, please try again.")

def logOutUser(id):

     updatedUser = userCollection.update({"_id": ObjectId(id) }, {"$set": { "active": False}})
     print("This is the updated users id", updatedUser)

     if(updatedUser == None or not updatedUser['updatedExisting']):
         raise Exception("Error occured during user log out, please try again.")





   

    
    



   
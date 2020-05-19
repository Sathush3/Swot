from flask_mail import Message

class MailService:

    @staticmethod
    def sendVerificationEmail(mail,recipient, userId):  
        
        msg = Message("Please Verify your email to continue with Music Annalyzer",
              recipients=[recipient])

        url = "http://127.0.0.1:5000/user/verify/%s" % userId
        print(url)
        msg.html = "<div> <p>Thank you for signing in with Music Annalyser, Click the button below to verify email</p><button><a href='%s'>Verify Email </a> </button></div>" % url

        mail.send(msg)

    @staticmethod 
    def sendUserResetEmail(mail, recipient, userId):
        
        msg = Message("[Reset] Music Annalyser - Reset Password",
              recipients=[recipient])

        msg.html ="<form action='http://localhost:5000/user/reset/%s' method='post'> <div class='container'><label for='new_pass'><b>New Password</b></label> <input type='password' placeholder='Enter Password' name='new_pass' required><label for='con_pass'><b>Retry Password</b></label><input type='password' placeholder='Enter Password' name='con_pass' required><button type='submit'>Reset</button></div></form>" % userId
    
        mail.send(msg)

        
        

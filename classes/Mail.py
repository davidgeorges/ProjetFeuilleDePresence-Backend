import smtplib
from config.config import settings
from email.message import EmailMessage
import ssl
from classes.Error import error

class Mail():

    #private members
    __msg = None
    __mail_sender = None
    __mail_server = None
    __mail_receiver = None
    __mail_subject = None
    __context = None

    def __init__(self):
        self.__msg = EmailMessage()
        self.__mail_sender = settings.MAIL_FROM
        self.__msg["From"] = self.__mail_sender
        self.__mail_server = None
        self.__mail_receiver = ""
        self.__mail_subject = ["Création de votre compte PresentS.","Récapitulatif des présences du"]
        self.__context = ssl.create_default_context()
              
    def set_mail_receiver(self,mail_receiver):
        self.__mail_receiver = mail_receiver
        if 'To' in self.__msg:
            self.__msg.replace_header('To', mail_receiver)
        else:
           self.__msg['To'] = mail_receiver

    def set_mail_subject(self,index):
        if 'Subject' in self.__msg:
            self.__msg.replace_header("Subject",self.__mail_subject[index])
        else:
            self.__msg["Subject"] = self.__mail_subject[index]

    def create_mail_server(self,smtpAddress,port):
        self.__mail_server = smtplib.SMTP_SSL(smtpAddress,port,context=self.__context)
        
    def login_into_mail_server(self,mail_login,mail_password):
        self.__mail_server.login(mail_login,mail_password)

    def send_mail(self):
        self.__mail_server.sendmail(self.__mail_sender,self.__mail_receiver,self.__msg.as_string())

    def set_mail_template(self,template):
       self.__msg.add_alternative(template, subtype = 'html')

    def send_login_info(self,user_mail,user_generated_password):

        self.set_mail_receiver([user_mail])

        mail_template = """
            <!DOCTYPE html>
            <html>
            <body>
                <div style="width:600px;">
                    <div style="display: flex;align-self: center;flex-direction: column;">
                        <image
                            src="https://upload.wikimedia.org/wikipedia/fr/thumb/6/69/Logo_CY_Cergy_Paris_Universit%C3%A9.svg/1200px-Logo_CY_Cergy_Paris_Universit%C3%A9.svg.png"
                            style="padding-top: 20px;padding-left: 20px;padding-right: 20px;padding-bottom: 20px;width:340px"></image>
                    </div>
                    <div >
                        <hr>
                        <p style="padding-top:10px;padding-left:10px;font-size: 24px;"><strong>Informations de votre compte</strong></p>
                        <p style="padding-top:10px;padding-left:10px;font-size: 20px;">Veuillez vous connecter avec les identifiants ci-dessous : </p>
                        <p style="padding-top:10px;padding-left:10px;font-size: 18px;">Mail : """+user_mail+"""</p>
                        <p style="padding-top:10px;padding-left:10px;font-size: 18px;">Mot de passe : """+user_generated_password+"""</p>
                    </div>
                    <div >
                        <p style="padding-top:10px;padding-left:10px;">@CY Cergy-Paris - 2022</p>
                    </div>
                </div>
            </body>
            </html>
                """
        
        self.set_mail_template(mail_template)
        self.set_mail_subject(0)
        self.send_mail()
        

mail = Mail()
try : 
    mail.create_mail_server(settings.MAIL_SERVER,settings.MAIL_PORT)
    mail.login_into_mail_server(settings.MAIL_USERNAME,settings.MAIL_PASSWORD)
except Exception as e:
    error.write_in_file("Error while creating mail server and login into mails --> "+str(e))
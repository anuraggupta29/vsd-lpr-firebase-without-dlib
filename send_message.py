from twilio.rest import Client

#--------------------------------------------------------------------

#this function will be completed and added later
def sendSMS():
    # Your Account Sid and Auth Token from twilio.com/console
    # DANGER! This is insecure. See http://twil.io/secure
    account_sid = 'account_sid'
    auth_token = 'auth_token'
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                         body="Your text here",
                         from_='twilio_number',#ANURAG GUPTA's twilio phone number
                         to='+91'+str("ENTER RECIEVER CONTACT NUMBER")
                     )

    return message.sid

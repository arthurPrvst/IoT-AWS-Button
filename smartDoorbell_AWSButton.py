from __future__ import print_function

import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
phone_number = '+xxxxxxxxxxx'  # change it to your phone number
ses = boto3.client('ses')
email_address = 'xxxxxx.xxxx@xx.x'  # change it to your email address


# Check if email is verified (You had to accept the request from AWS to your mail).
# Only verified emails are allowed to send emails to or from.
def check_email(email):
    result = ses.get_identity_verification_attributes(Identities=[email])
    attr = result['VerificationAttributes']
    if (email not in attr or attr[email]['VerificationStatus'] != 'Success'):
        logging.info('Verification email sent. Please verify it.')
        ses.verify_email_identity(EmailAddress=email)
        return False
    return True


#Handler that is called when AWS Button is pushed
def lambda_handler(event, context):
    logging.info('Received event: ' + json.dumps(event))
    clickType = event['clickType']
    if clickType == 'SINGLE': 
        # If it is a simple push on the button : send a SMS : "check your camera"
        message = 'We ring at your door ! Check your surveillance camera : http://fooBar.com/'
        sns.publish(PhoneNumber=phone_number, Message=message)
        logger.info('SMS has been sent to ' + phone_number)
    elif clickType == 'DOUBLE':
        #If it is a double push on the button : send an email to warn doorbell's owner
        if not check_email(email_address):
            logging.error('Mail : ERROR')
            return
    
        subject = 'Surveillance camera' 
        body_text = 'Check your surveillance camera : http://fooBar.com/'
        ses.send_email(Source=email_address,
                       Destination={'ToAddresses': [email_address]},
                       Message={'Subject': {'Data': subject}, 'Body': {'Text': {'Data': body_text}}})
        logger.info('Mail : OK')
    elif clickType == 'LONG':
        #If it is a long push on the button : send a SMS : "EMERGENCY : check your camera"
        message = 'EMERGENCY ! Check your surveillance camera : http://fooBar.com/'
        sns.publish(PhoneNumber=phone_number, Message=message)
        logger.info('SMS has been sent to ' + phone_number)

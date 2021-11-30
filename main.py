from __future__ import print_function
import os.path
from googleapiclient.discovery import build # pip install google-api-python-client
from google_auth_oauthlib.flow import InstalledAppFlow # google-auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from oauth2client.service_account import ServiceAccountCredentials # pip install oauth2client

SCOPES = ['https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/admin.directory.group']
GOOGLE_TOCHKAK_TOKEN = 'token.json'
DELEGATED_USER = 'admin@tochkak.ru'

def get_service(api_name, api_version, scopes, key_file_location):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_location, scopes)
    delegated_credentials = credentials.create_delegated(DELEGATED_USER)
    service = build(api_name, api_version, credentials=delegated_credentials)
    return service
#


def main():
    service = get_service(
            api_name='admin',
            api_version='directory_v1',
            scopes=SCOPES,
            key_file_location=GOOGLE_TOCHKAK_TOKEN)
    # results = service.users().list(domain='tochkak.ru', maxResults=10,
    #                                orderBy='email').execute()
    # print(results)
    user_json = {
        "languages": "ru",
        "isMailboxSetup": True,
        "primaryEmail": 'automate-test@tochkak.ru',
        "password": 'kinoplan',
        "name": {
          "givenName": "Эдуард", # First Name
          "fullName": "ПолноеИмя", # Full Name
          "familyName": "Вигерин", # Last Name
        },
        "changePasswordAtNextLogin": True
    }

    group_json = {
       "email": "automate@tochkak.ru",
       "name": "Automate Group",
       "description": "This is the Test automate group."
        }
    results = service.groups().list(userKey='vigerin@tochkak.ru').execute()
    # results = service.groups().insert(body=group_json).execute()
    # results = service.groups().list(memberKey='user@company.com').execute()


    print(results)
    #



if __name__ == '__main__':
    main()

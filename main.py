from unidecode import unidecode
import requests
import base64

import os.path
from googleapiclient.discovery import build # pip install google-api-python-client
from google_auth_oauthlib.flow import InstalledAppFlow # google-auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from oauth2client.service_account import ServiceAccountCredentials #  pip install oauth2client



SCOPES = ['https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/admin.directory.group']
GOOGLE_TOCHKAK_TOKEN = 'token.json'
DELEGATED_USER = 'admin@tochkak.ru'

DEBUG = True
global JIRA_HOST
JIRA_HOST = 'http://10.0.0.7:8080/'

jira_credentials = 'vigerin:wantt0Know'
jira_credentials_bytes = jira_credentials.encode('ascii')
JIRA_CREDENTIALS_BASE64 = base64.b64encode(jira_credentials_bytes).decode('ascii')


employee_name = 'Эдуард'
employee_surname = 'Вигерин'
employee_domain = 'tochkak.ru'
employee_position = 'sysadmin'

mail_groups  = {
    'vis': [
        'noc@dcp24.ru'
    ]
}


class Google:
    def create(self):
        token = ''
        def get_service(api_name, api_version, scopes, key_file_location):
            credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_location, scopes)
            delegated_credentials = credentials.create_delegated(DELEGATED_USER)
            service = build(api_name, api_version, credentials=delegated_credentials)
            return service
        #


class Jira:

    def create(self):
        api_call = 'rest/api/2/user'
        headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % JIRA_CREDENTIALS_BASE64}
        if DEBUG:
            print('headers = ', headers)
        data = {
            "name": self.latin_surname,
            "password": '',
            "emailAddress": self.mail,
            "displayName": self.surname + ' ' + self.name,
            "applicationKeys": [
            "jira-core"
            ]
        }
        if DEBUG:
            print('Params: ', self.latin_name, self.mail, self.latin_surname,self.surname + ' ' + self.name)
        create_user_request = requests.post(url=JIRA_HOST + api_call, headers=headers, json=data)
        if DEBUG:
            print(create_user_request.status_code)
            print(create_user_request.headers)
            print(create_user_request.text)
        if create_user_request.status_code == 201:
            if DEBUG:
                print("Пользователь создан в Jira")
            else:
                print("Пользователь не создан в Jira")
            return True

class Slack:
    def create(self, mail):
        return True

# Physical Access Control System, СКУД
class PACS:
    def create(self, name, surname, position, card_it):
        return True

class login:
    def create(self, name, surname, mail, position):
        return True


class Employee:
    def __init__(self, name, surname, domain, position):
        self.name = name.replace(' ', '')
        self.latin_name = unidecode(self.name).lower()
        self.surname = surname.replace(' ', '')
        self.latin_surname = unidecode(self.surname).lower()
        self.mail = self.latin_surname + '@' + domain
        if DEBUG:
            print('Будущая почта сотрудника: ', self.mail)
        self.position = position



def main():

    new_employee = Employee(employee_name, employee_surname, employee_domain, employee_position)
    new_jira_user = Jira.create(new_employee)

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
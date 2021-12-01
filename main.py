from unidecode import unidecode
import requests
import base64

# todo убери лишние импорты

import os.path
from googleapiclient.discovery import build # pip install google-api-python-client
from google_auth_oauthlib.flow import InstalledAppFlow # google-auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from oauth2client.service_account import ServiceAccountCredentials #  pip install oauth2client
import dicts



DEBUG = True

class Google:

    scopes = ['https://www.googleapis.com/auth/admin.directory.user',
              'https://www.googleapis.com/auth/admin.directory.group']
    api_name = 'admin'
    api_version = 'directory_v1'

    def get_service(key_file_location, delegated_user):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_location, Google.scopes)
        delegated_credentials = credentials.create_delegated(delegated_user)
        service = build(Google.api_name, Google.api_version, credentials=delegated_credentials)
        return service

    def create_user(self):
        user_json = {
            "languages": "ru",
            "isMailboxSetup": True,
            "primaryEmail": 'automate-test@tochkak.ru',
            "password": 'kinoplan',
            "name": {
                "givenName": "Эдуард",  # First Name
                "fullName": "ПолноеИмя",  # Full Name
                "familyName": "Вигерин",  # Last Name
            },
            "changePasswordAtNextLogin": True
        }
        print

    def add_to_group(self):
        print

    # возращает список групп
    def get_groups(self):
        # results = service.groups().list(userKey='vigerin@tochkak.ru').execute()
        # results = service.groups().insert(body=group_json).execute()
        # results = service.groups().list(memberKey='user@company.com').execute()
        print

    def get_group_members(self, group):
        print()

    # возвращает число пользователей
    def get_license_count(self):
        # число должно быть без алиасов
        print


class Jira:

    jira_host = 'http://10.0.0.7:8080/'

    jira_credentials = 'vigerin:wantt0Know'
    jira_credentials_bytes = jira_credentials.encode('ascii')
    JIRA_CREDENTIALS_BASE64 = base64.b64encode(jira_credentials_bytes).decode('ascii')

    def create(self):
        api_call = 'rest/api/2/user'
        headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % Jira.JIRA_CREDENTIALS_BASE64}
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
        create_user_request = requests.post(url=Jira.jira_host + api_call, headers=headers, json=data)
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


class Diagrams:
    def assign_place(self):
        return True

class Snipeit:
    def create_user(self):
        return True


class Employee:
    def __init__(self, name, surname, domain, position, location, mail_groups, jira_groups):
        self.name = name.replace(' ', '')
        self.latin_name = unidecode(self.name).lower()
        self.surname = surname.replace(' ', '')
        self.latin_surname = unidecode(self.surname).lower()
        self.domain = domain
        self.mail = self.latin_surname + '@' + domain
        self.location = location
        self.mail_groups = mail_groups
        self.jira_groups = jira_groups
        if DEBUG:
            print('Будущая почта сотрудника: ', self.mail)
        self.position = position




def main():
    # Задаем данные сотрудника
    # todo перепиши на чтобы брались из UI
    employee_name = 'Эдуард'
    employee_surname = 'Вигерин'
    employee_domain = 'tochkak.ru'
    employee_position = 'sysadmin'
    employee_location = 'S2'
    employee_pacs_id = '12 345678'
    employee_mail_groups = dicts.mail_groups['employee_position']
    employee_jira_groups = dicts.jira_groups_dict['employee_position']

    # создаем объект для сотрудника
    employee = Employee(
        employee_name,
        employee_surname,
        employee_domain,
        employee_position,
        employee_location,
        employee_mail_groups,
        employee_jira_groups)

    token_location = dicts.domain_props[employee.domain]['token']
    delegated_user = dicts.domain_props[employee.domain]['user']

    # создаем объект для авторизации
    service = Google.get_service(key_file_location=token_location, delegated_user=delegated_user)

    # создаем пользвоателя Google

    # создаем пользователя в Jira
    # new_jira_user = Jira.create(new_employee)



if __name__ == '__main__':
    main()
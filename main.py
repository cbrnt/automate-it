from unidecode import unidecode
import requests
import base64

import lists



global JIRA_HOST

DEBUG = True

JIRA_HOST = 'http://10.0.0.7:8080/'
jira_credentials = 'vigerin:wantt0Know'
jira_credentials_bytes = jira_credentials.encode('ascii')
JIRA_CREDENTIALS_BASE64 = base64.b64encode(jira_credentials_bytes).decode('ascii')


employee_name = 'Эдуард'
employee_surname = '               Вигерин'
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











if __name__ == '__main__':
    main()
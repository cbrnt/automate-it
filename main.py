from unidecode import unidecode
import requests
import base64


from googleapiclient.discovery import build # pip install google-api-python-client

from oauth2client.service_account import ServiceAccountCredentials #  pip install oauth2client
import dicts
import string
import random

DEBUG = False


class Google:

    scopes = ['https://www.googleapis.com/auth/admin.directory.user',
              'https://www.googleapis.com/auth/admin.directory.group']
    api_name = 'admin'
    api_version = 'directory_v1'

    @staticmethod
    def get_service(key_file_location, delegated_user):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_location, Google.scopes)
        delegated_credentials = credentials.create_delegated(delegated_user)
        service = build(Google.api_name, Google.api_version, credentials=delegated_credentials)
        return service

    @staticmethod
    def create_user(employee, service):
        user_json = {
            "languages": "ru",
            "isMailboxSetup": True,
            "primaryEmail": '%s' % employee.mail,
            "password": '%s' % employee.password,
            "name": {
                "givenName": "%s" % employee.name,  # First Name
                "fullName": "%s" % employee.name + ' ' + '%s' % employee.surname,  # Full Name
                "familyName": "%s" % employee.surname,  # Last Name
            },
            "changePasswordAtNextLogin": False
        }
        try:
            request_api = service.users().insert(body=user_json).execute()
            if DEBUG:
                print(request_api)
                print(request_api['primaryEmail'])
        except Exception as e:
            if DEBUG:
                print(type(e))
                print(e._get_reason())
            if e._get_reason() == 'Entity already exists.':
                error = 'Почта %s уже существует.' % employee.mail
                return error
        return True

    @staticmethod
    def add_to_group(employee, service, group):
        added_in_groups = list()
        not_added_in_groups = list()
        if DEBUG:
            print('Добавляю в группу %s' % group)
        try:
            group_json = {
                "kind": 'admin#directory#member',
                "email": employee.mail,
                "role": 'MEMBER'
            }
            request_api = service.members().insert(groupKey=group, body=group_json).execute()
            added_in_groups.append(group)
            if DEBUG:
                print(request_api)
                print(request_api['email'])
            print('Добавил в группу %s' % group)
        except Exception as e:
            if e._get_reason() == 'Member already exists.':
                error = 'Почта %s' % employee.mail + ' ' + 'уже есть в группе %s' % group
            else:
                error = e._get_reason()
            not_added_in_groups.append(group)
            return str(e._get_reason()), not_added_in_groups, error
        return added_in_groups

    # возращает список групп
    @staticmethod
    def get_groups(domain):
        token_path = dicts.domain_props[domain]['token']
        delegated_user = dicts.domain_props[domain]['user']
        service = Google.get_service(key_file_location=token_path, delegated_user=delegated_user)
        results = service.groups().list(domain=domain).execute()
        return results

    @staticmethod
    def get_group_members(domain, group):
        token_path = dicts.domain_props[domain]['token']
        delegated_user = dicts.domain_props[domain]['user']
        service = Google.get_service(key_file_location=token_path, delegated_user=delegated_user)
        results = service.members().list(groupKey=group).execute()
        return results

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
    def __init__(self, name, surname, domain, position, location, mail_groups, jira_groups, employee_pacs_id):
        self.name = name.replace(' ', '')
        self.latin_name = unidecode(self.name).lower()
        self.surname = surname.replace(' ', '')
        self.latin_surname = unidecode(self.surname).lower()
        self.domain = domain
        self.mail = self.latin_surname + '@' + domain
        self.location = location
        self.mail_groups = mail_groups
        self.jira_groups = jira_groups
        # k = длина пароля
        self.password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if DEBUG:
            print('Будущая почта сотрудника: ', self.mail)
        self.position = position
        # todo добавь форматирование кода
        self.pacs_id = employee_pacs_id

def main():
    # Задаем данные сотрудника
    # todo перепиши на чтобы брались из UI
    employee_name = 'Уатомат'
    employee_surname = 'ЫТ'
    employee_domain = 'tochkak.ru'
    employee_position = 'sysadmin'
    employee_location = 'S2'
    employee_pacs_id = '12 345678'
    employee_mail_groups = dicts.mail_groups.get(employee_position)
    employee_jira_groups = dicts.jira_groups_dict.get(employee_position)

    # создаем объект для сотрудника
    employee = Employee(
        employee_name,
        employee_surname,
        employee_domain,
        employee_position,
        employee_location,
        employee_mail_groups,
        employee_jira_groups,
        employee_pacs_id
    )

    token_location = dicts.domain_props[employee.domain]['token']
    delegated_user = dicts.domain_props[employee.domain]['user']

    # создаем объект для авторизации
    service = Google.get_service(key_file_location=token_location, delegated_user=delegated_user)

    # создаем пользователя Google
    create_gmail = Google.create_user(employee=employee, service=service)
    if create_gmail is True:
        print('Создана почта %s' % employee.mail)
    else:
        print('Почта не создана. Ошибка:' + ' ', create_gmail)
    # добавляем в группу, если есть в словаре mail_groups
    for group in employee.mail_groups:
        add_to_group = Google.add_to_group(employee, service, group)
        if len(add_to_group) == 1 and isinstance(add_to_group[0], list):
            print('Почта %s' % employee.mail + ' ' + 'добавлена в группы %s' % add_to_group)
        elif len(add_to_group) > 1 and add_to_group[2]:
            print('Группа %s' % add_to_group[1] + ' ' + 'Ошибка:' + ' ', add_to_group[2])
        elif len(add_to_group) > 1:
            print('Почта не добавлена в группу %s' % add_to_group[1] + ' ' + 'Ошибка:' + ' ', add_to_group[0])

    # создаем пользователя в Jira
    # new_jira_user = Jira.create(new_employee)

    # Выводим список групп и их членов
    # todo добавить указание домена
    for domain in dicts.domain_props.keys():
        equal_amount = len(str('Домен %s' % domain))
        print('=' * equal_amount)
        print('Домен %s' % domain)
        print('=' * equal_amount)
        groups_list = Google.get_groups(domain=domain)
        for group in range(len(groups_list.get('groups'))):
            print('    ' + groups_list.get('groups')[group].get('email') + ':')
            # выводим членов группы
            group_name = groups_list.get('groups')[group].get('email')
            get_group_member = Google.get_group_members(domain, group_name)

            for member in get_group_member.get('members'):
                if isinstance(member, dict):
                    print('       -', member['email'])







if __name__ == '__main__':
    main()
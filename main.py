from googleapiclient.errors import HttpError
from unidecode import unidecode
import requests
import base64
from googleapiclient.discovery import build  # pip install google-api-python-client
from oauth2client.service_account import ServiceAccountCredentials  # pip install oauth2client
import dicts
import string
import random
import logging
import argparse

DEBUG = False

parser = argparse.ArgumentParser()
parser.add_argument('--log', metavar='DEBUG',
                    dest='loglevel',
                    help='уровень логирования')
args = parser.parse_args()
if args.loglevel:
    LOGLEVEL = args.loglevel
else:
    LOGLEVEL = ''
# выставляем уровень логирования
log_file = 'automate-it.log'
numeric_level = getattr(logging, LOGLEVEL.upper(), None)
if not isinstance(numeric_level, int):
    logging.basicConfig(filename='%s' % log_file, level=logging.WARNING)
else:
    logging.basicConfig(filename='%s' % log_file, level=numeric_level)


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
        token_path = dicts.domain_attributes[domain]['token']
        delegated_user = dicts.domain_attributes[domain]['user']
        service = Google.get_service(key_file_location=token_path, delegated_user=delegated_user)
        results = service.groups().list(domain=domain).execute()
        return results

    @staticmethod
    def get_group_members(domain, group):
        token_path = dicts.domain_attributes[domain]['token']
        delegated_user = dicts.domain_attributes[domain]['user']
        service = Google.get_service(key_file_location=token_path, delegated_user=delegated_user)
        results = service.members().list(groupKey=group).execute()
        return results

    # возвращает число пользователей
    @staticmethod
    def get_license_count(domain):
        scopes = ['https://www.googleapis.com/auth/apps.licensing']
        api_name = 'licensing'
        api_version = 'v1'
        token_path = dicts.domain_attributes[domain]['token']
        delegated_user = dicts.domain_attributes[domain]['user']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(token_path, scopes)
        delegated_credentials = credentials.create_delegated(delegated_user)
        service = build(api_name, api_version, credentials=delegated_credentials)
        results = service.licenseAssignments().listForProduct(productId='Google-Apps', customerId=domain).execute()
        return len(results.get('items'))


class GoogleSheets:
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # Токен только tochkak.ru, так как лазить буду только туда
    token_file = 'keys/tochkak_token.json'

    # The ID and range of a sample spreadsheet.

    delegated_user = 'admin@tochkak.ru'

    def get_service(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.token_file, GoogleSheets.SCOPES)
        delegated_credentials = credentials.create_delegated(self.delegated_user)
        try:
            service = build('sheets', 'v4', credentials=delegated_credentials)
        except HttpError as err:
            logging.error('Ошибка при получении доступа к Sheets', err)
        return service



def get_all_groups():
    for domain in dicts.domain_attributes.keys():
        equal_amount = len(str('Домен %s' % domain))
        print('=' * equal_amount)
        print('Домен %s' % domain)
        print('=' * equal_amount)
        groups_list = Google.get_groups(domain=domain)
        print('Число групп: ', len(groups_list.get('groups')))
        for group in range(len(groups_list.get('groups'))):
            print('    ' + groups_list.get('groups')[group].get('email') + ':')
            # выводим членов группы
            group_name = groups_list.get('groups')[group].get('email')
            get_group_member = Google.get_group_members(domain, group_name)

            for member in get_group_member.get('members', '1'):
                if isinstance(member, dict):
                    print('       -', member.get('email'))
                else:
                    print('       -' + 'пустая группа')


def main():
    # # Задаем данные сотрудника
    # employee_name = 'Уатомат'
    # employee_surname = 'ЫТ'
    # employee_domain = 'tochkak.ru'
    # employee_position = 'sysadmin'
    # employee_location = 'S2'
    # employee_pacs_id = '12 345678'
    # employee_mail_groups = dicts.mail_groups.get(employee_position)
    # employee_jira_groups = dicts.jira_groups_dict.get(employee_position)
    #
    # # создаем объект для сотрудника
    # employee = Employee(
    #     employee_name,
    #     employee_surname,
    #     employee_domain,
    #     employee_position,
    #     employee_location,
    #     employee_mail_groups,
    #     employee_jira_groups,
    #     employee_pacs_id
    # )
    #
    # token_location = dicts.domain_props[employee.domain]['token']
    # delegated_user = dicts.domain_props[employee.domain]['user']

    # создаем объект для авторизации
    # service = Google.get_service(key_file_location=token_location, delegated_user=delegated_user)
    #
    # # создаем пользователя Google
    # create_gmail = Google.create_user(employee=employee, service=service)
    # if create_gmail is True:
    #     print('Создана почта %s' % employee.mail)
    # else:
    #     print('Почта не создана. Ошибка:' + ' ', create_gmail)
    # # добавляем в группу, если есть в словаре mail_groups
    # for group in employee.mail_groups:
    #     add_to_group = Google.add_to_group(employee, service, group)
    #     if len(add_to_group) == 1 and isinstance(add_to_group[0], list):
    #         print('Почта %s' % employee.mail + ' ' + 'добавлена в группы %s' % add_to_group)
    #     elif len(add_to_group) > 1 and add_to_group[2]:
    #         print('Группа %s' % add_to_group[1] + ' ' + 'Ошибка:' + ' ', add_to_group[2])
    #     elif len(add_to_group) > 1:
    #         print('Почта не добавлена в группу %s' % add_to_group[1] + ' ' + 'Ошибка:' + ' ', add_to_group[0])
    #
    # # создаем пользователя в Jira
    # # new_jira_user = Jira.create(new_employee)
    #
    # # Выводим список групп и их членов
    # # get_all_groups()

    # Запрашиваю количество лицензий
    for domain in dicts.domain_attributes.keys():
        get_licenses = Google.get_license_count(domain)
        print('Занятых лицензий на домене %s' % domain + ': ', get_licenses)

    # пишем в Sheets
    sheet_id = '1BBFVl6QFvRrkSRyPTnmtjWlfhkXwBbAZ32_Zgvi0sBM'
    append_range = 'A1:A2'
    valueInputOption = 'RAW'
    sheets = GoogleSheets
    try:
        sheet_service = sheets.get_service(sheets)
        sheet = sheet_service.spreadsheets()
        request_body = {
            "range": "%s" % append_range,
            "majorDimension": "COLUMNS",
            "values": [
                ['Tochkak.ru',
                'vigerin@tochkak.ru']
            ]
        }
        result = sheet.values().append(spreadsheetId=sheet_id,
                                       range=append_range,
                                       body=request_body,
                                       valueInputOption=valueInputOption).execute()

    except HttpError as err:
        logging.error('Ошибка при работе с таблицами', err)


if __name__ == '__main__':
    main()

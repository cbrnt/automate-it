import os.path

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
    @staticmethod
    def get_license_count(domain):
        scopes = ['https://www.googleapis.com/auth/apps.licensing']
        api_name = 'licensing'
        api_version = 'v1'
        token_path = dicts.domain_props[domain]['token']
        if os.path.exists(token_path):
            delegated_user = dicts.domain_props[domain]['user']
            credentials = ServiceAccountCredentials.from_json_keyfile_name(token_path, scopes)
            delegated_credentials = credentials.create_delegated(delegated_user)
            service = build(api_name, api_version, credentials=delegated_credentials)
            results = service.licenseAssignments().listForProduct(productId='Google-Apps', customerId=domain).execute()
            return len(results.get('items'))

    @staticmethod
    def get_users(service_obj, domain_str) -> list():
        users_json = service_obj.users().list(domain=domain_str).execute()
        user_list = []
        for user in users_json['users']:
            user_list.append([user['name']['fullName'], user['primaryEmail']])
        return user_list


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
    for domain in dicts.domain_props.keys():
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


def put_captions(service, sheet_id, valueInputOption):
    """Пишет заголовки в начало таблицы"""
    count = 1
    for domain in dicts.domain_props:
        caption_range = 'Users!R1C%s' % count
        caption_request_body = {
            "range": "%s" % caption_range,
            "majorDimension": "ROWS",
            "values": [
                ['%s' % domain]
            ]
        }
        count += 3
        caption_create_result = service.values().append(spreadsheetId=sheet_id,
                                                      range=caption_range,
                                                      body=caption_request_body,
                                                      valueInputOption=valueInputOption).execute()


def put_licenses(service, sheet_id, valueInputOption):
    """Пишет сколько занято лицензий в начало таблицы"""
    count = 1
    for domain in dicts.domain_props:
        licenses = Google.get_license_count(domain)
        caption_range = 'Users!R1C%s' % count
        caption_request_body = {
            "range": "%s" % caption_range,
            "majorDimension": "ROWS",
            "values": [
                ['Занятых лицензий: %s' % licenses]
            ]
        }
        count += 3
        caption_create_result = service.values().append(spreadsheetId=sheet_id,
                                                      range=caption_range,
                                                      body=caption_request_body,
                                                      valueInputOption=valueInputOption).execute()


def main():
    # собираем пользователей по всем доменам
    user_dict = {}
    for domain in dicts.domain_props:
        try:
            if os.path.exists(dicts.domain_props[domain]['token']):
                service = Google.get_service(key_file_location=dicts.domain_props[domain]['token'], delegated_user=dicts.domain_props[domain]['user'])
                user_dict[domain] = Google.get_users(service, domain)
        except HttpError as err:
            logging.error('Ошибка в запросе к Mail', err)

    # готовимся писать в Sheets
    sheets = GoogleSheets()
    sheet_id = '1BBFVl6QFvRrkSRyPTnmtjWlfhkXwBbAZ32_Zgvi0sBM'
    tabs_range_list = ['Users!A1:Z1000', 'Groups!A1:Z1000']
    valueInputOption = 'RAW'
    try:
        sheet_service = sheets.get_service()
        sheet = sheet_service.spreadsheets()
        # Получаем диапазон заполненных ячеек
        for tab in tabs_range_list:
            # очищаем таблицы по списку
            clear = sheet.values().clear(spreadsheetId=sheet_id,
                                        range=tab).execute()
        # Добавляем заголовки
        put_captions(sheet, sheet_id, valueInputOption)
        # добавляем количество лицензий
        put_licenses(sheet, sheet_id, valueInputOption)
        # определяем область для записи
        append_range = 'Users!A1:B%s' % str(user_dict.__len__())
        request_body_caption = {
            "range": "%s" % append_range,
            "majorDimension": "ROWS",
            "values": user_dict
        }
        result = sheet.values().append(spreadsheetId=sheet_id,
                                       range=append_range,
                                       body=request_body_caption,
                                       valueInputOption=valueInputOption).execute()
    except HttpError as err:
        logging.error('Ошибка при работе с таблицами', err)


if __name__ == '__main__':
    main()

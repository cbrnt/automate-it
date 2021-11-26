from unidecode import unidecode
import requests


global JIRA_HOST

JIRA_HOST = 'http://10.0.0.7:8080/'
JIRA_CREDENTIALS = 'vigerin:wantt0Know'


position_dict = {
    'developer': 'Разработчик',
    'vis': 'Оператор ВИС',
    'trader': 'Менеджер по продажам',
    'qa': 'Тестировщик',
    'scrum': 'SCRUM-мастер',
    'bill': 'Бухгалтер',
    'backend': 'Backend разработчик',
    'frontend': 'Frontend разработчик',
    'writer': 'Технический писатель',
    'manager': 'Менеджер продуктов',
    'sysadmin': 'Системный администратор'
}

jira_groups_dict = {
    'developer': [
        'confluence-users', 'kinoplan_onboarding', 'stash-users'
    ],
    'backend': [
        'confluence-users', 'kinoplan_onboarding', 'stash-users'
    ],
    'frontend': [
        'confluence-users', 'kinoplan_onboarding', 'stash-users'
    ],
}

mail_groups  = {
    'vis': [
        'noc@dcp24.ru'
    ]
}

class Employee:
    def __init__(self, name, surname, mail, position):
        self.name = name
        self.latin_name = unidecode(name)
        self.surname = surname
        self.latin_surname = unidecode(surname)
        self.mail = mail
        self.position = position

class Jira:
    def check_user_exist(self, mail):
        api_call = 'rest/api/2/user/search'
        headers = {'Content-Type': 'application/json'}
        params = {
            'username': '%s' % mail,
            'maxResults': 1
        }
        get_user_list = requests.get(url=JIRA_HOST + api_call, headers=headers, params=params)
        print(get_user_list.headers)
        print(get_user_list.text)




def main():
    new_employee = Employee('Эдуард', 'Вигерин', 'tochkak.ru', 'sysadmin')
    print(new_employee)
    jira_check = Jira()
    jira_check.check_user_exist('vigeri@tochkak.ru')









if __name__ == '__main__':
    main()
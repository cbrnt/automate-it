
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

mail_groups = {
    'vis': [
        'noc@dcp24.ru'
    ],
    'sysadmin': [
        'it@tochkak.ru'
    ]
}

# domain_props = {
#     'tochkak.ru': {
#         'token': 'keys/tochkak_token.json',
#         'user': 'admin@tochkak.ru'
#     },
#     'dcp24.ru': {
#         'token': 'keys/dcp24_token.json',
#         'user': 'admin@dcp24.ru'
#     },
#     'kinoplan.ru': {
#         'token': 'keys/kinoplan_token.json',
#         'user': 'admin@kinoplan.ru'
#     }
# }

domain_props = {
    'tochkak.ru': {
        'token': 'keys/tochkak_token.json',
        'user': 'admin@tochkak.ru'
    }
}

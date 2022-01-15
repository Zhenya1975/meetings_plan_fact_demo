import pandas as pd

# читаем исходный файл из загрузки
rb_events_raw_data = pd.read_csv('data/rb_events_df.csv')

# читаем исходный файл из загрузки клиентов
rb_companies_raw_data = pd.read_csv('data/rb_companies_df.csv')

user_id = 1
users_list = []
user_code_list = []
user_code_user_id_values = {}
for index, row in rb_companies_raw_data.iterrows():
    temp_dict = {}
    temp_dict['user_id'] = user_id
    user_code = row['ФИО инициалы']
    temp_dict['user_code'] = user_code
    name_position = row['Ответственный менеджер'].split(',')
    temp_dict['name'] = name_position[0]
    if len(name_position)>1:
        temp_dict['position'] = name_position[1]
    else:
        temp_dict['position'] = "менеджер"
    if temp_dict['user_code'] not in user_code_list:
        user_code_list.append(user_code)
        users_list.append(temp_dict)
        user_code_user_id_values[user_code] = user_id
        user_id += 1
users_df = pd.DataFrame(users_list)

print(user_code_user_id_values)
# в таблице встреч создаем новую колонку, равную Ответственный
# rb_events_raw_data['user_id'] = rb_events_raw_data['Ответственный']
# подставляем вместо user_code значение user_id

rb_events_raw_data['user_id'] = rb_events_raw_data['Ответственный'].map(user_code_user_id_values)
# rb_events_raw_data = rb_events_raw_data.astype({"user_id": int})

print(rb_events_raw_data['user_id'])
# протягиваем id пользователя в таблице встреч
# values = {"plan_date": '01.01.1970', "close_date": '01.01.1970'}
#     closed_events = closed_events.copy()
#     closed_events.fillna(value=values, inplace=True)


#print(users_df)




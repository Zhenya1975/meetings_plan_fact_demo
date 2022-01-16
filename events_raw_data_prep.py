import pandas as pd

# читаем исходный файл из загрузки
rb_events_raw_data = pd.read_csv('data/rb_events_df.csv')

# читаем исходный файл из загрузки клиентов
rb_companies_raw_data = pd.read_csv('data/rb_companies_df.csv')

# выкидываем строки где нет ответственного
rb_events_with_responsible = rb_events_raw_data.dropna(subset=['Ответственный'])
# выкидываем строки где нет связанного клиента
rb_events_with_responsible_and_customers = rb_events_with_responsible.dropna(subset=['ID клиента'])

user_id = 1
users_list = []
user_code_list = []
user_id_list = []
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
        user_id_list.append(user_id)
        user_code_user_id_values[user_code] = user_id
        user_id += 1
user_id = max(user_id_list)

for index, row in rb_events_with_responsible_and_customers.iterrows():
    temp_dict = {}
    user_code = row['Ответственный']
    temp_dict['user_id'] = user_id
    temp_dict['user_code'] = user_code
    temp_dict['name'] = user_code
    temp_dict['position'] = row['Должность ответственного']
    if temp_dict['user_code'] not in user_code_list:
        user_code_list.append(user_code)
        users_list.append(temp_dict)
        user_id_list.append(user_id)
        user_code_user_id_values[user_code] = user_id
        user_id += 1

users_df = pd.DataFrame(users_list)
users_df.to_csv('data/users.csv')
# print(users_df)
# print(user_code_user_id_values)

# подставляем вместо user_code значение user_id аналог ВПР
rb_events_with_responsible_and_customers = rb_events_with_responsible_and_customers.copy()
rb_events_with_responsible_and_customers['user_id'] = rb_events_with_responsible_and_customers['Ответственный'].map(user_code_user_id_values)

rb_events_with_responsible_and_customers = rb_events_with_responsible_and_customers.astype({"user_id": int, 'ID клиента': int})
rb_events_with_responsible_and_customers.to_csv('data/rb_events_with_responsible_and_customers_delete.csv')


rb_companies_raw_data = rb_companies_raw_data.copy()
rb_companies_raw_data['user_id'] = rb_companies_raw_data['ФИО инициалы'].map(user_code_user_id_values)

# заполняем нулями пустые значения в поле Область
empty_regions = {"Область": 'нд',}
rb_companies_raw_data = rb_companies_raw_data.copy()
rb_companies_raw_data.fillna(value=empty_regions, inplace=True)

# Протягиваем коды регионов по наименованию областей
regions_df = pd.read_csv('Data/regions.csv')
region_dict = {}
for index, row in regions_df.iterrows():
    region_dict[row['region_name']] = row['region_code']
rb_companies_raw_data['region_code'] = rb_companies_raw_data['Область'].map(region_dict)



# переименовываем колонки
rb_companies_raw_data = rb_companies_raw_data.rename(columns={
        "ID":"customer_id",
        "Наименование":"customer_name",
        "Область":"region_name",
        "Дата завершения":"Close_date",
        "Потенциал продаж с/х техники. Сегмент":"segment_letter",
        "ФИО инициалы":"user_code"
    })
rb_companies_raw_data.to_csv('data/rb_companies_raw_data_delete.csv')
# формируем файл customers_df
customers_df = rb_companies_raw_data.loc[:, ['customer_id', "customer_name", "region_code", "region_name", "user_id", "user_code", "segment_letter"]]
customers_df.to_csv('data/customers.csv')




# протягиваем id пользователя в таблице встреч
# values = {"plan_date": '01.01.1970', "close_date": '01.01.1970'}
# closed_events = closed_events.copy()
# closed_events.fillna(value=values, inplace=True)






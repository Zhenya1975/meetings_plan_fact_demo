import pandas as pd

# читаем исходный файл из загрузки
rb_events_raw_data = pd.read_csv('data/rb_events_df.csv')

# читаем исходный файл из загрузки клиентов
rb_companies_raw_data = pd.read_csv('data/rb_companies_df.csv')

user_id = 1
users_list = []
for index, row in rb_companies_raw_data.iterrows():
    temp_dict = {}
    temp_dict['user_id']
    temp_dict['user_id'] = user_id


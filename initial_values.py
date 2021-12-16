import datetime
import pandas as pd
import json

mode = 'actual'
# mode = 'demo'

if mode == 'demo':
    events_df = pd.read_csv('Data/demo_events.csv')
    customer_df = pd.read_csv('Data/demo_customers.csv')
    users_df = pd.read_csv('Data/demo_users.csv')
    segments_visit_plan = pd.read_csv('Data/segments_visits_plans_demo.csv')
else:
    events_df = pd.read_csv('Data/events.csv')
    customer_df = pd.read_csv('Data/customers.csv')
    users_df = pd.read_csv('Data/users.csv')
    segments_visit_plan = pd.read_csv('Data/segments_visits_plans_demo.csv')

def customers_visit_plan():
    """Список клиентов и план их посещений"""
    customer_visit_plan_df = pd.merge(customer_df, segments_visit_plan, on='segment_letter', how='left')
    return customer_visit_plan_df

def get_curent_quarter_and_year():
    """получение текущего квартала и года"""
    current_date = datetime.datetime.now()
    """текущая дата в формате datetime"""

    current_quarter = round((current_date.month - 1) / 3)
    """номер текущего квартала"""

    current_year = current_date.year
    """Номер текущего года"""
    return current_quarter, current_year

def closed_events_prep(events_df):
    # сначала удаляем пустые строки встреч без связи с клиентом
    events_df.dropna(subset=['region_name', 'customer_id'], inplace=True)
    values = {"deal_id": 0}
    events_df = events_df.copy()
    events_df.fillna(value=values, inplace=True)
    events_df = events_df.astype({"deal_id": int, 'customer_id': int})
    # добавляем колонки "visit_fact" c нулями. И "plan_fact_status" c нулями
    events_df['visits_fact'] = 0
    events_df['plan_fact_status'] = 0

    # удаляем строки без даты завершения. Это будет датафрейм closed_events
    closed_events_df = events_df.dropna(subset=['close_date'])
    # в таблицу customers добавляем колонку "visits_fact" и заполняем ее нулями
    customer_df['visits_fact'] = 0

    # нам нужны строки со статусом "Завершен" и с периодом текущего квартала.
    # сначала удаляем строки, в которых поле close_date не заполнено
    closed_events = events_df.dropna(subset=['close_date'])

    #  заполняем пустые поля с датами значением  '01.01.1970'
    values = {"plan_date": '01.01.1970', "close_date": '01.01.1970'}
    closed_events = closed_events.copy()
    closed_events.fillna(value=values, inplace=True)

    # Протягиваем коды регионов по наименованию областей
    regions_df = pd.read_csv('Data/regions.csv')
    region_dict = {}
    for index, row in regions_df.iterrows():
        region_dict[row['region_name']] = row['region_code']
    closed_events['region_code'] = closed_events['region_name'].map(region_dict)

    # протягиваем цифру 1 в поле qty. Понадобятся для подсчета строк
    closed_events['qty'] = 1
    # заполняем оставшиеся пустые ячейки
    closed_events.fillna(value={"region_code": 0, 'region_name': 'н.д.', 'deal_id': 0}, inplace=True)

    closed_events = closed_events.astype({"deal_id": int, 'region_code': int})

    # конвертируем даты в даты
    closed_events = closed_events.copy()
    date_column_list = ['close_date']
    for date_column in date_column_list:
        closed_events.loc[:, date_column] = pd.to_datetime(closed_events[date_column], infer_datetime_format=True, format='%d.%m.%Y')
        closed_events.loc[:, date_column] = closed_events.loc[:, date_column].apply(lambda x: datetime.date(x.year, x.month, x.day))
    # сортируем по колонке close_event
    closed_events.sort_values(['close_date'], inplace=True)
    return closed_events
closed_events = closed_events_prep(events_df)

#  собираем данные о менеджерах и регионах из events
def prepare_users_list():
    # events_df = pd.read_csv('Data/events.csv')
    # list_of_users = events_df.loc[:, ['user_id']]
    # list_of_unique_users - список уникальных пользователей в таблице встреч

    list_of_unique_users = pd.DataFrame(customer_df['user_id'].unique(), columns=['user_id'])
    result_df_list = []
    # итерируемся по списку уникальных пользователей
    for index, row_user_id in list_of_unique_users.iterrows():
        dict_temp = {}
        user_id = row_user_id['user_id']
        # temp_df - выборка из таблицы встреч по текущему юзеру в цикле
        temp_df = events_df.loc[events_df['user_id']==user_id]
        user_region_list = []
        # итерируемся по полученной выборке и собираем все регионы, которые нам попадутся
        for index, row_events_selection in temp_df.iterrows():
            region_code = row_events_selection['region_code']
            #if region_code !=0 and region_code not in user_region_list:
            if region_code not in user_region_list:
                user_region_list.append(region_code)
        customer_temp_df = customer_df[customer_df['user_id'] == user_id]
        for index, row_events_selection in customer_temp_df.iterrows():
            region_code = row_events_selection['region_code']
            #if region_code !=0 and region_code not in user_region_list:
            if region_code not in user_region_list:
                user_region_list.append(region_code)
        # Проверяем. Если список регионов у юзера пустой, то даем ему регион с кодом ноль
        if len(user_region_list) == 0:
            dict_temp['user_id'] = user_id
            dict_temp['regions_list'] = [0]
        else:
            dict_temp['user_id'] = user_id
            dict_temp['regions_list'] = user_region_list
        # добавляем пользователя в список
        result_df_list.append(dict_temp)
    user_region_df = pd.DataFrame(result_df_list)
    user_region_df.to_csv('Data/user_regions.csv')

    return list_of_unique_users

prepare_users_list()

def get_users_regions_df():
    if mode == 'actual':
        users_regions_df= pd.read_csv('Data/user_regions.csv')
    else:
        users_regions_df = pd.read_csv('Data/user_regions_demo.csv')
    # из СSV список делаем списком
    users_regions_df['regions_list'] = users_regions_df['regions_list'].apply(lambda x: json.loads(x))

    return users_regions_df
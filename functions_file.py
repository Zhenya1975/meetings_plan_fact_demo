from datetime import date, timedelta
from calendar import monthrange
import pandas as pd
import initial_values
import datetime
import numpy as np


def quarter_important_days(quarter_number, year):
    """quarter_important_days() получает на вход номер квартала и год. 4 и 2021. На выходе отдает первый день и последний запрашиваемого квартала"""
    first_month_of_quarter = 3 * quarter_number - 2
    last_month_of_quarter = 3 * quarter_number
    date_of_first_day_of_quarter = date(year, first_month_of_quarter, 1)
    date_of_last_day_of_quarter = date(year, last_month_of_quarter, monthrange(year, last_month_of_quarter)[1])
    return date_of_first_day_of_quarter, date_of_last_day_of_quarter

def cut_df_by_dates_interval(df, date_field_name, start_date, end_date):
    """Выборка в диапазоне дат. Пример: date_field_name: 'close_date',  start_date, end_date - в формате datetime.date"""
    start_date = start_date
    end_date = end_date
    after_start_date = df.loc[:, date_field_name] >= start_date
    before_end_date = df.loc[:, date_field_name] <= end_date
    between_two_dates = after_start_date & before_end_date
    result_df = df.loc[between_two_dates]
    return result_df

def quarter_all_dates_prepare(first_day_of_selection, last_day_of_selection):
    """список всех дней квартала с полем qty = 0. Заготовка для построения графика факта"""
    result_df = pd.DataFrame([first_day_of_selection+timedelta(days=x) for x in range((last_day_of_selection-first_day_of_selection).days)], columns=['close_date'])
    result_df['zero_qty'] = 0
    return result_df

def check_user_in_region(a, b):
  return not set(a).isdisjoint(b)

def get_unique_users(df_selections, region_list_value, managers_from_checklist):
    """получение данные для чек-боксов пользователей"""

    users_unique_list = pd.DataFrame(df_selections['user_id'].unique(), columns=['user_id'])
    # users_regions_df - код юзера - список регионов
    users_regions_df = initial_values.get_users_regions_df()

    # region_list - список регионов, выбранных в фильтрах.
    region_list = region_list_value

    # нужно ответить на вопрос есть ли юзеры в списке users_unique_list в выбранных регионах
    # джойним users_unique_list с users_regions_df

    users_unique_list_with_regions = pd.merge(users_unique_list, users_regions_df, on='user_id', how='left')

    user_list_cut_by_regions = []
    for index, row in users_unique_list_with_regions.iterrows():
        a = row['regions_list']
        b = region_list
        if check_user_in_region(a, b):
            user_list_cut_by_regions.append(row['user_id'])


    user_list_cut_by_regions_df = pd.DataFrame(user_list_cut_by_regions, columns=['user_id'])
    mode = initial_values.mode
    users_full = initial_values.initial_values_init(mode)[2]
    users_with_names = pd.merge(user_list_cut_by_regions_df, users_full, on='user_id', how='left')
    users_with_names.sort_values('name', inplace=True)

    users_checklist_data = []
    users_list = []
    for index, row in users_with_names.iterrows():
        dict_temp = {}
        dict_temp['label'] = " " + str(row['name']) + ', ' + str(row['position'])
        dict_temp['value'] = row['user_id']
        users_checklist_data.append(dict_temp)
        users_list.append(row['user_id'])
    return users_checklist_data, user_list_cut_by_regions


def quarter_days(quarter_selector_value, year_selector_value):
    # создаем выборку по кварталу - либо по текущему по умолчанию, либо по выбранному пользователем
    current_date = datetime.datetime.now()
    """текущая дата в формате datetime"""

    today = datetime.datetime.now().date()
    """текущая дата в формате date"""

    current_quarter = round((current_date.month - 1) / 3)
    """номер текущего квартала"""

    current_year = current_date.year
    """Номер текущего года"""

    requested_quarter = quarter_selector_value
    """номер квартала из инпута на странице отчета. По умолчанию - текущий"""

    requested_year = year_selector_value
    """Номер года из инпута на странице отчета. По умолчанию - текущий"""

    if requested_year == current_year and requested_quarter == current_quarter:
        first_day_of_selection = quarter_important_days(requested_quarter, requested_year)[0]
        """Если запрошенный год и квартал равен текущему, первый день выборки - это первый день квартала"""
        last_day_of_selection = today
        """Если запрошенный год и квартал равен текущему, последний день выборки - это текущий день. Иначе -последний день квартала"""
    else:
        first_day_of_selection = quarter_important_days(requested_quarter, requested_year)[0]
        last_day_of_selection = quarter_important_days(requested_quarter, requested_year)[1]
    return first_day_of_selection, last_day_of_selection

def regions_checklist_data(df):
    '''подготовка данных для чек-листа регионов'''
    region_list_closed = df['region_code']
    regions_unique_list = pd.DataFrame(region_list_closed.unique(), columns=['region_code'])
    # left join кодов регионов и наименований регионов
    regions_full = pd.read_csv('Data/regions.csv')
    regions_with_names = pd.merge(regions_unique_list, regions_full, on='region_code', how='left')
    regions_with_names.sort_values('region_name', inplace=True)

    region_checklist_data = []
    region_list = []
    for index, row in regions_with_names.iterrows():
        dict_temp = {}
        dict_temp['label'] = " " + row['region_name']
        dict_temp['value'] = row['region_code']
        region_checklist_data.append(dict_temp)
        region_list.append(row['region_code'])
    return region_checklist_data, region_list

def plan_fact_df_prep(events_df_selected_by_quarter_ready, meetings_data_selector):
    # Cписок клиентов с планом посещений
    customer_visit_plan_df = initial_values.customers_visit_plan()

    # получаем данные по динамике выполнения плана
    customer_visit_plan = customer_visit_plan_df.loc[:, ['customer_id', 'visit_plan']]
    events_df_selected_by_quarter_ready_with_plan = pd.merge(events_df_selected_by_quarter_ready, customer_visit_plan, on='customer_id', how='left')

    # выкидываем строки со встречами, в которых нет клиентов
    events_df_selected_by_quarter_ready_with_plan.dropna(subset=['customer_id'], inplace=True)
    # меняем тип данных в int
    events_df_selected_by_quarter_ready_with_plan = events_df_selected_by_quarter_ready_with_plan.astype(
        {'user_id': int, 'event_id': int, "customer_id": int, 'visit_plan': int})

    # Выкидываем строки, в которых план равен 0. Такие встречи не должны влиять на выполнение плана
    events_df_selected_by_quarter_ready_with_plan = events_df_selected_by_quarter_ready_with_plan.loc[events_df_selected_by_quarter_ready_with_plan['visit_plan'] > 0]


    # нужно посчитать агргированное значение по клиентам
    result_df_list = []
    # В дикт customer_user_visit_fact будем записывать накопленные значения сумм визитов по пользователю и клиенту
    customer_user_visit_fact = {}
    events_df_selected_by_quarter_ready_with_plan['customer_user_id'] = events_df_selected_by_quarter_ready_with_plan['customer_id'].astype(str) + '_' + events_df_selected_by_quarter_ready_with_plan['user_id'].astype(str)

    for index, row in events_df_selected_by_quarter_ready_with_plan.iterrows():
        temp_dict = {}
        event_id = row['event_id']
        customer_user_id = row['customer_user_id']
        if customer_user_id in customer_user_visit_fact:
            customer_user_visit_fact[customer_user_id] += 1
        else:
            customer_user_visit_fact[customer_user_id] = 1
        temp_dict['event_id'] = event_id
        temp_dict['cum_value'] = customer_user_visit_fact[customer_user_id]
        result_df_list.append(temp_dict)
    cum_fact_df = pd.DataFrame(result_df_list)

    df = pd.merge(cum_fact_df, events_df_selected_by_quarter_ready_with_plan, on='event_id', how='left')


    # plan_fact_cum_result = pd.merge(cum_fact_df, events_df_selected_by_quarter_ready_with_plan, how='left', on='event_id')

    df['delta'] = df['visit_plan']-df['cum_value']
    df['status'] = np.where(df['delta'] <=0, 1, 0)

    if meetings_data_selector == 'include_plan_fact_meetings':
         # удаляем строки в которых количество cum_value больше плана, то есть встречи сверх плана
         df = df.loc[df['cum_value'] > df['visit_plan']]



    ###### Данные для таблицы

    plan_fact_cum_result_groupped = df.groupby(['customer_id', 'user_id'], as_index=False).agg({'visit_plan': 'max', 'qty': 'sum' })
    plan_fact_cum_result_groupped.rename(columns={'qty': 'visit_fact'}, inplace=True)

    plan_fact_cum_result_groupped['delta'] = plan_fact_cum_result_groupped['visit_plan'] - plan_fact_cum_result_groupped['visit_fact']
    plan_fact_cum_result_groupped['status'] = np.where(plan_fact_cum_result_groupped['delta'] <= 0, 1, 0)


    return df, plan_fact_cum_result_groupped

def events_demo_prepare(df):
    """перезапись events.df и подготовка данных для events_demo"""
    df.to_csv('Data/events.csv')
    # подготовка demo_events - перезапись комментов
    demo_comments = pd.read_csv('Data/communications.csv')
    result_list = []
    for index, row in df.iterrows():
        temp_dict = {}
        temp_dict['event_id'] = row['event_id']
        temp_dict['user_id'] = row['user_id']
        temp_dict['user_code'] = row['user_code']
        temp_dict['plan_date'] = row['plan_date']
        temp_dict['close_date'] = row['close_date']
        temp_dict['customer_id'] = row['customer_id']
        temp_dict['region_name'] = row['region_name']
        temp_dict['region_code'] = row['region_code']
        temp_dict['deal_id'] = row['deal_id']
        sample_comment_df = demo_comments.sample(ignore_index=True)
        sample_description = sample_comment_df.iloc[0]['Описание']
        sample_close_comment = sample_comment_df.iloc[0]['Чем завершилось']
        temp_dict['description'] = sample_description
        if row['close_date'] == "":
            temp_dict['close_comment'] = sample_close_comment
        else:
            temp_dict['close_comment'] = row['close_comment']

        result_list.append(temp_dict)
    demo_events_df = pd.DataFrame(result_list)
    demo_events_df.to_csv('Data/demo_events.csv')
    # запуск функций initials_values
    # mode = initial_values.mode


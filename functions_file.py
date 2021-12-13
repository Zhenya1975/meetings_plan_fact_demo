from datetime import date, timedelta
from calendar import monthrange
import pandas as pd
import initial_values


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
    users_full = initial_values.users_df
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
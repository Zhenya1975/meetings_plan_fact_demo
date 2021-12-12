import functions_file
import initial_values
import pandas as pd
import datetime

import meetings_plan_fact_graph_data_prepare


def prepare_meetings_fact_data(quarter_selector_value, year_selector_value, selected_regions):
    # получаем таблицу events / demo_events
    if initial_values.mode == 'demo':
        events_df = pd.read_csv('Data/demo_events.csv')
    else:
        events_df = pd.read_csv('Data/events.csv')


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

    # протягиаем цифру 1 в поле qty. Понядобятся для подсчета строк
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

    # создаем выборку по квараталу - либо по текущему по умолчанию, либо по выбранному пользователем
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
        first_day_of_selection = functions_file.quarter_important_days(requested_quarter, requested_year)[0]
        """Если запрошенный год и квартал равен текущему, первый день выборки - это первый день квартала"""
        last_day_of_selection = today
        """Если запрошенный год и квартал равен текущему, последний день выборки - это текущий день. Иначе -последний день квартала"""
    else:
        first_day_of_selection = functions_file.quarter_important_days(requested_quarter, requested_year)[0]
        last_day_of_selection = functions_file.quarter_important_days(requested_quarter, requested_year)[1]

    quarter_all_dates_df = functions_file.quarter_all_dates_prepare(first_day_of_selection, last_day_of_selection)


    events_df_selected_by_quarter = functions_file.cut_df_by_dates_interval(closed_events, 'close_date', first_day_of_selection, last_day_of_selection)

    # датафрем по закрытым ивентам в выбранный квартал подготовлен.
    # Выбираем из него поля и эту заготовку отправляем на работу по построению графиков
    events_df_selected_by_quarter_ready = events_df_selected_by_quarter.loc[:, ['event_id', 'user_id', 'user_code', 'plan_date', 'close_date', 'customer_id', 'region_name', 'region_code', 'deal_id', 'description', 'close_comment', 'qty']]
    events_df_selected_by_quarter_ready = events_df_selected_by_quarter_ready.reset_index(drop=True)

    # получаем данные для чек-листа регионов
    """получаем данные для чек-боксов регионов"""
    region_list_closed = events_df_selected_by_quarter_ready['region_code']
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


    return events_df_selected_by_quarter_ready, region_checklist_data, region_list, quarter_all_dates_df, first_day_of_selection, last_day_of_selection






import functions_file
import initial_values
import pandas as pd
import datetime


def prepare_meetings_fact_data(quarter_selector_value, year_selector_value, selected_regions, meetings_data_selector):
    customer_df = initial_values.customer_df
    events_df = initial_values.closed_events_df
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

    # Cписок клиентов с планом посещений
    customer_visit_plan_df = initial_values.customers_visit_plan()

    # получаем данные по динамике выполнения плана
    customer_visit_plan = customer_visit_plan_df.loc[:, ['customer_id', 'visit_plan']]
    events_df_selected_by_quarter_ready_with_plan = pd.merge(events_df_selected_by_quarter_ready, customer_visit_plan, on='customer_id', how='left')
    fact_result_list = []
    user_customer_fact_dict = {}
    for index, row in events_df_selected_by_quarter_ready_with_plan.iterrows():
        dict_temp = {}
        dict_temp['event_id'] = row['event_id']
        dict_temp['user_id'] = row['user_id']
        dict_temp['close_date'] = row['close_date']
        dict_temp['customer_id'] = row['customer_id']
        dict_temp['region_code'] = row['region_code']
        dict_temp['deal_id'] = row['deal_id']
        dict_temp['description'] = row['description']
        dict_temp['close_comment'] = row['close_comment']
        dict_temp['qty'] = row['qty']
        customer_id = row['customer_id']
        customer_plan = row['visit_plan']
        user_id = row['user_id']
        user_customer_id = str(user_id) + '_' + str(customer_id)
        dict_temp['user_customer_id'] = user_customer_id
        if user_customer_id in user_customer_fact_dict and user_customer_fact_dict[user_customer_id] < customer_plan:
            user_customer_fact_dict[user_customer_id] += 1
        else:
            user_customer_fact_dict[user_customer_id] = 1
        dict_temp['visit_plan'] = row['visit_plan']
        dict_temp['prev_fact'] = user_customer_fact_dict[user_customer_id] -1
        dict_temp['fact'] = user_customer_fact_dict[user_customer_id]
        if user_customer_fact_dict[user_customer_id] >= row['visit_plan']:
            dict_temp['plan_fact_status'] = 1
        else:
            dict_temp['plan_fact_status'] = 0
        fact_result_list.append(dict_temp)

    events_plan_fact_df = pd.DataFrame(fact_result_list)
    if meetings_data_selector == 'include_plan_fact_meetings':
        # удаляем строки в которых предыдущий факт больше или равен плана. То есть уже норма выполнена
        events_plan_fact_df = events_plan_fact_df.loc[events_plan_fact_df['visit_plan'] > events_plan_fact_df['prev_fact']]



    return events_plan_fact_df, region_checklist_data, region_list, quarter_all_dates_df, first_day_of_selection, last_day_of_selection, customer_visit_plan_df






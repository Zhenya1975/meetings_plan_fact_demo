from datetime import date
from calendar import monthrange


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
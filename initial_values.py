import datetime

# mode = 'actual'
mode = 'demo'

def get_curent_quarter_and_year():
    """получение текущего квартала и года"""
    current_date = datetime.datetime.now()
    """текущая дата в формате datetime"""

    current_quarter = round((current_date.month - 1) / 3)
    """номер текущего квартала"""

    current_year = current_date.year
    """Номер текущего года"""
    return current_quarter, current_year

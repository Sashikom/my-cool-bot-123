# sheets.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ——— Настройка доступа ———
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gc = gspread.authorize(credentials)

# ——— Получение таблицы и первого листа ———
def get_sheet():
    spreadsheet = gc.open_by_key('1Ae1QlpVqmD8ADE0wUkqfXgMV8Ri4Ty5dmBCJySYct64')
    return spreadsheet.sheet1

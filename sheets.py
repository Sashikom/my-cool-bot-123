import os
import gspread
from google.oauth2 import service_account

def get_sheet():
    file_path = os.getenv("GS_CREDENTIALS_JSON_FILE")
    sheet_name = os.getenv("SPREADSHEET_NAME")

    if not file_path or not sheet_name:
        raise EnvironmentError("⛔️ Не указаны переменные окружения GS_CREDENTIALS_JSON_FILE или SPREADSHEET_NAME")

    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = service_account.Credentials.from_service_account_file(file_path, scopes=scope)
        client = gspread.authorize(credentials)
        spreadsheet = client.open(sheet_name)
        # Можно получить первый лист
        worksheet = spreadsheet.sheet1
        # Или, если хотите по имени листа, например:
        # worksheet = spreadsheet.worksheet("Лист1")
        return worksheet
    except Exception as e:
        import logging
        logging.error(f"Ошибка подключения к Google Sheets: {e}")
        return None

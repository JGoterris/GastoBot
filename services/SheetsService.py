import gspread
from gspread.spreadsheet import Spreadsheet
from google.oauth2.service_account import Credentials

class SheetsService:
    def __init__(self, credentials_path: str) -> None:
        scopes = [ "https://www.googleapis.com/auth/spreadsheets" ]
        creds = Credentials.from_service_account_file("creds.json", scopes=scopes)
        self.client = gspread.authorize(creds)
    
    def get_sheet_by_id(self, sheetId: str) -> Spreadsheet:
        sheet = self.client.open_by_key(sheetId)
        return sheet

import gspread
from gspread.spreadsheet import Spreadsheet
from google.oauth2.service_account import Credentials
import locale
from datetime import datetime
from utils.JsonUtil import to_list

class SheetsService:
    def __init__(self, credentials_path: str, sheet_id: str) -> None:
        scopes = [ "https://www.googleapis.com/auth/spreadsheets" ]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.get_sheet_by_id(sheet_id)

        # Configurar formato fechas
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Linux/Mac
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')  # Windows
            except:
                pass  # Usar inglés por defecto
    
    def get_sheet_by_id(self, sheetId: str) -> Spreadsheet:
        sheet = self.client.open_by_key(sheetId)
        return sheet
    
    def upload_new_row(self, json_data: str):
        worksheet = self.get_or_create_monthly_sheet()
        worksheet.append_row(to_list(json_data))
    
    def get_month_year_name(self, date=None):
        if date is None:
            date = datetime.now()
        
        # Formato: "Enero 2024"
        return date.strftime("%B %Y").title()
    
    def get_or_create_monthly_sheet(self, month_year=None):
        if month_year is None:
            month_year = self.get_month_year_name()
        
        try:
            # Intentar obtener la hoja existente
            worksheet = self.sheet.worksheet(month_year)
            print(f"Hoja '{month_year}' encontrada")
            return worksheet
        
        except gspread.WorksheetNotFound:
            # Crear nueva hoja si no existe
            print(f"Creando nueva hoja: '{month_year}'")
            worksheet = self.sheet.add_worksheet(
                title=month_year,
                rows=1000,
                cols=10
            )
            
            # Configurar encabezados
            headers = [
                "Establecimiento", "Importe", "Descripción", 
                "Fecha", "Categoria"
            ]
            worksheet.append_row(headers)
            
            # Formatear encabezados
            worksheet.format('A1:E1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
            })
            
            return worksheet
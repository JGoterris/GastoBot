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
                "Fecha", "Categoría"
            ]
            worksheet.append_row(headers)
            
            # Formatear encabezados
            worksheet.format('A1:E1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
            })
            
            return worksheet
        
    def get_monthly_summary(self, month_year=None):
        """Obtiene resumen de gastos del mes"""
        try:
            worksheet = self.get_or_create_monthly_sheet(month_year)
            
            # Obtener todos los datos (excepto encabezados)
            all_records = worksheet.get_all_records()
            
            if not all_records:
                return
            
            # Calcular totales por categoría
            category_totals = {}
            total_month = 0
            
            for record in all_records:
                categoria = record.get('Categoría', 'Sin categoría')
                monto = float(record.get('Importe', 0.00)[:-1])
                
                category_totals[categoria] = category_totals.get(categoria, 0) + monto
                total_month += monto
            
            # Crear resumen
            summary = f"📊 Resumen de {worksheet.title}:\n\n"
            summary += f"💰 Total del mes: {total_month:.2f} €\n\n"
            summary += "📋 Por categorías:\n"
            
            for categoria, total in category_totals.items():
                percentage = (total / total_month) * 100 if total_month > 0 else 0
                summary += f"• {categoria}: {total:.2f} € ({percentage:.1f}%)\n"
            
            return summary
            
        except Exception as e:
            return
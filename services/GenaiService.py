from google import genai
from dotenv import load_dotenv

load_dotenv()

class GenaiService:
    EXTRACTION_PROMPT = """Extrae un json con los campos: establecimiento, importe, 
    descripcion y categoria. Esta última tienes que elegir entre: ocio, ropa, 
    comida, necesidad, amigos, fiesta o varios.
    Si algún campo no tienes información suficiente, pon el campo en blanco, no te inventes la información.
    No lo pongas en formato markdown ni 
    agregues ningun texto, devuelve el json en raw (no incluyas ```json). """

    def __init__(self):
        self.client = genai.Client()
    
    def basic_request(self, text: str):
        prompt = text + " " + self.EXTRACTION_PROMPT
        response = self.client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt)
        return response.text
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GenaiService:
    EXTRACTION_PROMPT = """Extrae un json con los campos: establecimiento, importe (formato: Número.Decimales €), 
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

    def audio_request(self, audio_path: str):
        try:
            audio_file = self.client.files.upload(file=audio_path)
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    audio_file,
                    self.EXTRACTION_PROMPT
                ]
            )
            
            self.client.files.delete(name=audio_file.name)
            
            return response.text
            
        except Exception as e:
            print(f"Error procesando audio: {e}")
            return None
        
    def image_request(self, image_path: str):
        try:
            image_file = self.client.files.upload(file=image_path)

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[image_file, self.EXTRACTION_PROMPT]
            )

            self.client.files.delete(name=image_file.name)

            return response.text

        except Exception as e:
            print(f"Error procesando imagen: {e}")
            return None
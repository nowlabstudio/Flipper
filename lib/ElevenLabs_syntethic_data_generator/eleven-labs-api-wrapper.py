"""
Eleven Labs API Wrapper

Ez a modul egyszerű wrapper funkciókat biztosít az Eleven Labs API-hoz való hozzáféréshez.
A kulcsszó-felismerési projekthez szükséges API végpontokat tartalmazza.
"""

import requests
import json
import time
from pathlib import Path

class ElevenLabsAPI:
    """
    Eleven Labs API-hoz való hozzáférést biztosító osztály.
    """
    
    def __init__(self, config_path="config/keyword_generation_config.json"):
        """
        Inicializálja az API wrapper-t a konfigurációs fájlból.
        
        Args:
            config_path: A konfigurációs fájl elérési útja
        """
        # Konfiguráció betöltése
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        # API kulcs és URL-ek kinyerése
        self.api_key = self.config["api"]["eleven_labs_api_key"]
        self.base_url = self.config["api"]["base_url"]
        self.tts_url = self.config["api"]["tts_url"]
        self.sound_gen_url = self.config["api"]["sound_gen_url"]
        
        # Generálási paraméterek
        self.voice_settings = {
            "stability": self.config["generation_params"]["stability"],
            "similarity_boost": self.config["generation_params"]["similarity_boost"],
            "style": self.config["generation_params"]["style"],
            "use_speaker_boost": self.config["generation_params"]["use_speaker_boost"]
        }
        
        # Alap header
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Kimeneti könyvtár biztosítása
        output_dir = Path(self.config["output"]["directory"])
        output_dir.mkdir(exist_ok=True)
    
    def verify_voice(self, voice_id):
        """
        Ellenőrzi a hangot az API-nál.
        
        Args:
            voice_id: A hang azonosítója
            
        Returns:
            A hang neve vagy None hiba esetén
        """
        try:
            response = requests.get(
                f"{self.base_url}/voices/{voice_id}",
                headers={"xi-api-key": self.api_key}
            )
            
            if response.status_code == 200:
                return response.json()["name"]
            else:
                print(f"Hiba a hang ellenőrzésekor: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"Kivétel a hang ellenőrzésekor: {e}")
            return None
    
    def text_to_speech(self, text, voice_id, output_path):
        """
        Szöveget beszéddé alakít az Eleven Labs TTS API használatával.
        
        Args:
            text: A beszéddé alakítandó szöveg
            voice_id: A használandó hang azonosítója
            output_path: A kimeneti fájl elérési útja
            
        Returns:
            A temporális fájl elérési útja vagy None hiba esetén
        """
        data = {
            "text": text,
            "model_id": self.config["generation_params"]["model_id"],
            "voice_settings": self.voice_settings,
            "output_format": self.config["generation_params"]["output_format"]
        }
        
        try:
            response = requests.post(
                f"{self.tts_url}/{voice_id}/stream",
                json=data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                # Ideiglenes mp3 fájl mentése
                temp_path = output_path.with_suffix('.mp3')
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                return temp_path
            else:
                print(f"Hiba a beszéd generálásakor: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"Kivétel a beszéd generálásakor: {e}")
            return None
    
    def generate_background_noise(self, description):
        """
        Háttérzajt generál az Eleven Labs Sound Generation API használatával.
        
        Args:
            description: A generálandó hang leírása
            
        Returns:
            A generált hang bájtos tartalma vagy None hiba esetén
        """
        data = {
            "text": description
        }
        
        try:
            response = requests.post(
                self.sound_gen_url,
                json=data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Hiba a háttérzaj generálásakor: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"Kivétel a háttérzaj generálásakor: {e}")
            return None
    
    def test_api_connection(self):
        """
        Teszteli az API kapcsolatot.
        
        Returns:
            True, ha a kapcsolat működik, False egyébként
        """
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers={"xi-api-key": self.api_key}
            )
            
            if response.status_code == 200:
                voices = response.json()
                print(f"API kapcsolat működik. {len(voices.get('voices', []))} hang érhető el.")
                return True
            else:
                print(f"API kapcsolat hiba: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"API kapcsolat kivétel: {e}")
            return False

    def get_all_voices(self):
        """
        Lekéri az összes elérhető hangot az API-ról.
        
        Returns:
            A hangok listája vagy üres lista hiba esetén
        """
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers={"xi-api-key": self.api_key}
            )
            
            if response.status_code == 200:
                return response.json().get("voices", [])
            else:
                print(f"Hiba a hangok lekérésekor: {response.status_code}")
                print(response.text)
                return []
        except Exception as e:
            print(f"Kivétel a hangok lekérésekor: {e}")
            return []

def main():
    """
    Teszteli az Eleven Labs API wrapper működését.
    """
    print("Eleven Labs API Wrapper teszt")
    print("-" * 50)
    
    # API wrapper inicializálása
    api = ElevenLabsAPI()
    
    # API kapcsolat tesztelése
    if not api.test_api_connection():
        print("Hiba: Nem sikerült kapcsolódni az Eleven Labs API-hoz.")
        return
    
    # Hangok lekérése
    print("\nHangok lekérése az API-ról...")
    voices = api.get_all_voices()
    if voices:
        print(f"{len(voices)} hang érhető el az API-n:")
        for i, voice in enumerate(voices[:5]):  # Csak az első 5 hang
            print(f"{i+1}. {voice.get('name')} (ID: {voice.get('voice_id')})")
        if len(voices) > 5:
            print(f"... és még {len(voices) - 5} hang.")
    
    # Konfigurációban lévő hangok ellenőrzése
    print("\nKonfigurációban lévő hangok ellenőrzése:")
    for i, voice in enumerate(api.config["voices"][:3]):  # Csak az első 3 hang
        api_voice_name = api.verify_voice(voice["id"])
        status = "✓" if api_voice_name else "✗"
        print(f"{i+1}. {voice['name']} (ID: {voice['id']}): {status}")
    
    print("\nA teljes API wrapper funkció teszteléséhez használd a fő generáló szkriptet.")

if __name__ == "__main__":
    main()

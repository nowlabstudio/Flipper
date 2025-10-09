"""
Eleven Labs hang beállítások gyűjtése

Ez a szkript lekérdezi a megadott hangot az Eleven Labs API-ból,
és eltárolja a releváns beállításokat egy JSON fájlban.
Lehetőséget ad további hangok paramétereinek hozzáadására is.
"""

import requests
import json
import os
import sys
from pathlib import Path
import argparse

class VoiceSettingsCollector:
    """
    Eleven Labs hangok beállításainak gyűjtéséhez és tárolásához használt osztály.
    """
    
    def __init__(self, api_key, voices_file="voice_settings.json"):
        """
        Inicializálja a gyűjtőt.
        
        Args:
            api_key: Az Eleven Labs API kulcs
            voices_file: A JSON fájl, amelyben a beállításokat tároljuk
        """
        self.api_key = api_key
        self.voices_file = Path(voices_file)
        
        # Inicializáljuk az üres voice_settings szótárat
        self.voice_settings = {}
    
    def get_voice_details(self, voice_id):
        """
        Lekérdezi egy hang részleteit az Eleven Labs API-ból.
        
        Args:
            voice_id: A hang azonosítója
            
        Returns:
            A hang adatai, vagy None hiba esetén
        """
        url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
        headers = {"xi-api-key": self.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Hiba a hang lekérdezésekor: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"Kivétel a hang lekérdezésekor: {e}")
            return None
    
    def extract_voice_settings(self, voice_data):
        """
        Kinyeri a releváns beállításokat a hang adataiból.
        
        Args:
            voice_data: A hang API-ból lekérdezett adatai
            
        Returns:
            Szótár a releváns beállításokkal
        """
        settings = {}
        
        # Alap adatok
        settings["name"] = voice_data.get("name", "Ismeretlen")
        settings["id"] = voice_data.get("voice_id", "")
        
        # Modell adatok
        settings["model"] = "eleven_multilingual_v2"  # Alapértelmezett modell
        
        # Hang beállítások
        voice_settings = voice_data.get("settings", {})
        settings["speed"] = voice_settings.get("speed", 1.0)
        settings["stability"] = voice_settings.get("stability", 0.5)
        settings["similarity_boost"] = voice_settings.get("similarity_boost", 0.75)
        settings["style_exaggeration"] = voice_settings.get("style", 0.0)
        settings["speaker_boost"] = voice_settings.get("use_speaker_boost", True)
        
        return settings
    
    def add_voice_settings(self, voice_id, custom_settings=None):
        """
        Hozzáad egy hang beállítást a gyűjteményhez.
        
        Args:
            voice_id: A hang azonosítója
            custom_settings: Egyéni beállítások (opcionális)
            
        Returns:
            True, ha sikeres, False egyébként
        """
        # Töröljük a korábbi hang beállításokat
        self.voice_settings = {}
        
        # Ha vannak egyéni beállítások, azokat használjuk
        if custom_settings:
            print(f"Egyéni beállítások használata a hanghoz: {voice_id}")
            self.voice_settings[voice_id] = custom_settings
            return True
        
        # Egyébként lekérdezzük a hangot az API-ból
        print(f"Hang lekérdezése az API-ból: {voice_id}")
        voice_data = self.get_voice_details(voice_id)
        
        if not voice_data:
            print(f"Hiba: Nem sikerült lekérdezni a hangot: {voice_id}")
            return False
        
        # Hang beállítások kinyerése
        settings = self.extract_voice_settings(voice_data)
        
        # Hang beállítások mentése
        self.voice_settings[voice_id] = settings
        
        print(f"Hang beállítások sikeresen hozzáadva: {settings['name']} ({voice_id})")
        return True
    
    def save_settings(self):
        """
        Elmenti a hang beállításokat egy JSON fájlba.
        
        Returns:
            True, ha sikeres, False egyébként
        """
        try:
            with open(self.voices_file, "w", encoding="utf-8") as f:
                json.dump(self.voice_settings, f, indent=4, ensure_ascii=False)
            
            print(f"Hang beállítások sikeresen mentve: {self.voices_file}")
            return True
        except Exception as e:
            print(f"Hiba a beállítások mentésekor: {e}")
            return False
    
    def print_voice_settings(self, voice_id=None):
        """
        Kiírja a hang beállításokat.
        
        Args:
            voice_id: A megjelenítendő hang azonosítója (opcionális)
        """
        if voice_id:
            # Csak egy hang beállításainak megjelenítése
            if voice_id in self.voice_settings:
                settings = self.voice_settings[voice_id]
                print(f"\nHang beállítások: {settings['name']} ({voice_id})")
                print("-" * 50)
                print(f"- Név: {settings['name']}")
                print(f"- ID: {settings['id']}")
                print(f"- Modell: {settings['model']}")
                print(f"- Sebesség: {settings['speed']}")
                print(f"- Stabilitás: {settings['stability']}")
                print(f"- Hasonlóság: {settings['similarity_boost']}")
                print(f"- Stílus túlzás: {settings['style_exaggeration']}")
                print(f"- Beszélő kiemelés: {settings['speaker_boost']}")
            else:
                print(f"Hiba: A hang ({voice_id}) nem található a gyűjteményben.")
        else:
            # Minden hang beállításának megjelenítése
            print(f"\nÖsszes hang beállítás ({len(self.voice_settings)}):")
            for vid, settings in self.voice_settings.items():
                print("-" * 50)
                print(f"Hang: {settings['name']} ({vid})")
                print(f"- Modell: {settings['model']}")
                print(f"- Sebesség: {settings['speed']}")
                print(f"- Stabilitás: {settings['stability']}")
                print(f"- Hasonlóság: {settings['similarity_boost']}")
                print(f"- Stílus túlzás: {settings['style_exaggeration']}")
                print(f"- Beszélő kiemelés: {settings['speaker_boost']}")

def get_api_key_from_config():
    """
    Megpróbálja kinyerni az API kulcsot a konfigurációból.
    
    Returns:
        Az API kulcs, vagy None ha nem található
    """
    config_paths = [
        "config/keyword_generation_config.json",
        "keyword_generation_config.json"
    ]
    
    for path in config_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
                api_key = config.get("api", {}).get("eleven_labs_api_key", "")
                if api_key:
                    return api_key
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    
    return None

def get_presets():
    """
    Előre definiált beállítások megadott hangokhoz.
    
    Returns:
        Szótár a hang ID-k és beállításaik mappelésével
    """
    return {
        "TumdjBNWanlT3ysvclWh": {
            "name": "Magyar Férfi - Hungarian Male",
            "id": "TumdjBNWanlT3ysvclWh",
            "model": "eleven_multilingual_v2",
            "speed": 1.0,
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style_exaggeration": 0.0,
            "speaker_boost": True
        }
    }

def add_voice_cli(collector, voice_id, use_presets=True):
    """
    Interaktív módon hozzáad egy hang beállítást a gyűjteményhez.
    
    Args:
        collector: A VoiceSettingsCollector példány
        voice_id: A hang azonosítója
        use_presets: Használjunk-e előre definiált beállításokat
        
    Returns:
        True, ha sikeres, False egyébként
    """
    # Próbáljuk meg használni az előre definiált beállításokat
    if use_presets:
        presets = get_presets()
        if voice_id in presets:
            print(f"Előre definiált beállítások használata a hanghoz: {voice_id}")
            return collector.add_voice_settings(voice_id, presets[voice_id])
    
    # Ha nincs előre definiált beállítás, lekérdezzük az API-ból
    return collector.add_voice_settings(voice_id)

def main():
    parser = argparse.ArgumentParser(description="Eleven Labs hang beállítások gyűjtése")
    parser.add_argument("--voice", "-v", help="A hang azonosítója")
    parser.add_argument("--output", "-o", default="voice_settings.json", 
                        help="A kimeneti JSON fájl")
    parser.add_argument("--api-key", "-k", help="Eleven Labs API kulcs")
    parser.add_argument("--list", "-l", action="store_true",
                        help="Listázza a gyűjteményben lévő hangokat")
    parser.add_argument("--preset", "-p", action="store_true",
                        help="Használja az előre definiált beállításokat")
    
    args = parser.parse_args()
    
    print("Eleven Labs hang beállítások gyűjtése")
    print("=" * 50)
    
    # API kulcs meghatározása
    api_key = args.api_key
    if not api_key:
        api_key = get_api_key_from_config()
        if not api_key:
            api_key = input("Add meg az Eleven Labs API kulcsot: ").strip()
    
    if not api_key:
        print("Hiba: Nem adtál meg API kulcsot.")
        sys.exit(1)
    
    # Gyűjtő inicializálása
    collector = VoiceSettingsCollector(api_key, args.output)
    
    # Ha listázást kértek
    if args.list:
        collector.print_voice_settings()
        sys.exit(0)
    
    # Ha megadtak hang azonosítót
    if args.voice:
        if add_voice_cli(collector, args.voice, args.preset):
            collector.save_settings()
            collector.print_voice_settings(args.voice)
        sys.exit(0)
    
    # Interaktív mód
    while True:
        print("\nVálassz műveletet:")
        print("1. Új hang hozzáadása")
        print("2. Hangok listázása")
        print("3. Beállítások mentése")
        print("0. Kilépés")
        
        choice = input("\nVálasztás: ").strip()
        
        if choice == "1":
            voice_id = input("Add meg a hang azonosítóját: ").strip()
            add_voice_cli(collector, voice_id, args.preset)
        elif choice == "2":
            collector.print_voice_settings()
        elif choice == "3":
            collector.save_settings()
        elif choice == "0":
            print("Kilépés...")
            collector.save_settings()
            break
        else:
            print("Érvénytelen választás!")

if __name__ == "__main__":
    main()

"""
Eleven Labs API - Multi Speed Generator Script

Ez a szkript létrehoz különböző sebességű hangfájlokat az Eleven Labs API-n keresztül
az összes bekapcsolt hanggal, felhasználva a megadott voice_settings.json konfigurációt.
A sebesség variációk száma a --speed paraméterrel állítható, egyenlően elosztva 0.7 és 1.2 között.
"""

import json
import time
import argparse
from pathlib import Path
import sys
import os
import importlib.util
import requests
import numpy as np

# Dinamikus importálás a fájl tényleges nevéből
wrapper_filename = "eleven-labs-api-wrapper.py"
if os.path.exists(wrapper_filename):
    module_name = "eleven_labs_api"
    spec = importlib.util.spec_from_file_location(module_name, wrapper_filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    ElevenLabsAPI = module.ElevenLabsAPI
else:
    # Próbáljuk meg közvetlenül importálni, ha a modulnév helyes
    try:
        from eleven_labs_api import ElevenLabsAPI
    except ImportError:
        print("Hiba: Nem található az eleven_labs_api modul.")
        print("Ellenőrizd, hogy létezik-e eleven_labs_api.py vagy eleven-labs-api-wrapper.py fájl.")
        sys.exit(1)

def load_enabled_voices(file_path):
    """
    Betölti az engedélyezett (enabled=true) hangokat a json fájlból
    
    Args:
        file_path: A voice_settings.json fájl elérési útja
        
    Returns:
        Az engedélyezett hangok listája és a teljes JSON tartalom
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            voice_settings = json.load(f)
            
        # Ellenőrizzük, hogy van-e tartalom
        if not voice_settings:
            print("Hiba: A voice_settings.json fájl üres.")
            sys.exit(1)
            
        # Kiválasztjuk az engedélyezett hangokat
        enabled_voices = []
        for key, voice in voice_settings.items():
            # Ellenőrizzük, hogy a hang enabled=true beállítással rendelkezik-e
            if voice.get("enabled", False) == True:
                enabled_voices.append(voice)
        
        if not enabled_voices:
            print("Hiba: Nem található engedélyezett hang a voice_settings.json fájlban.")
            print("Legalább egy hanghoz állítsd be az 'enabled': true értéket.")
            sys.exit(1)
            
        print(f"{len(enabled_voices)} engedélyezett hang található a voice_settings.json fájlban.")
        return enabled_voices, voice_settings
    except Exception as e:
        print(f"Hiba a voice_settings.json betöltése során: {e}")
        sys.exit(1)

def generate_speech_with_different_speeds(api_key, voice_id, text, voice_name, num_speeds=3, 
                                         stability=0.32, similarity_boost=0.1, style=0.0, speaker_boost=True):
    """
    Közvetlenül generál beszédet különböző sebességekkel az Eleven Labs API-n keresztül.
    
    Args:
        api_key: Az Eleven Labs API kulcsa
        voice_id: A hang azonosítója
        text: A beszéddé alakítandó szöveg
        voice_name: A hang neve (fájlnév generálásához)
        num_speeds: A generálandó sebességvariációk száma
        stability: A stabilitás értéke
        similarity_boost: A hasonlóság erősítés értéke
        style: A stílus értéke
        speaker_boost: A beszélő erősítés bekapcsolása
    """
    # Kimeneti könyvtár létrehozása
    output_dir = Path("generated_speeches")
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    # Sebességek generálása egyenletes eloszlással 0.7 és 1.2 között
    min_speed = 0.7
    max_speed = 1.2
    
    # Egyenlő lépésközökkel generáljuk a sebességeket a megadott tartományban
    speeds = np.linspace(min_speed, max_speed, num_speeds).tolist()
    speeds = [round(speed, 2) for speed in speeds]  # Kerekítés 2 tizedesjegyre
    
    # Alapvető API beállítások
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    print(f"\nHangfájlok generálása \"{text}\" szöveggel, {voice_name} hanggal, {len(speeds)} különböző sebességgel")
    print(f"Sebességértékek: {speeds}")
    print(f"Kimeneti könyvtár: {output_dir}")
    print("-" * 60)
    
    # Minden sebességgel generálunk egy hangfájlt
    for speed in speeds:
        # Fájlnév generálása
        safe_name = ''.join(c for c in voice_name if c.isalnum())
        output_filename = f"{safe_name}_speed_{speed:.2f}_{int(time.time())}.mp3"
        output_path = output_dir / output_filename
        
        print(f"\nGenerálás {speed:.2f}x sebességgel")
        print(f"Kimeneti fájl: {output_path}")
        
        # Kérés összeállítása
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": speaker_boost,
                "speed": speed
            }
        }
        
        try:
            # API hívás
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                # Ha sikeres, mentjük a hangfájlt
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"Beszéd sikeresen generálva {speed:.2f}x sebességgel: {output_path}")
            else:
                print(f"Hiba a beszéd generálása során: {response.status_code}")
                print(f"Hibaüzenet: {response.text}")
        except Exception as e:
            print(f"Kivétel a beszéd generálása során: {e}")
    
    print("\nA hangfájlok sikeresen elkészültek!")

def main():
    parser = argparse.ArgumentParser(description="Eleven Labs Multi Speed Generator")
    parser.add_argument("--config", "-c", default="config/keyword_generation_config.json", 
                        help="A konfigurációs fájl elérési útja")
    parser.add_argument("--voice_settings", "-v", default="voice_settings.json",
                        help="A voice_settings.json fájl elérési útja")
    parser.add_argument("--text", "-t", 
                        default=None,
                        help="A beszéddé alakítandó szöveg (ha nincs megadva, alapértelmezett szöveg lesz)")
    parser.add_argument("--speed", "-s", type=int, default=3,
                        help="Hány különböző sebességvariációt generáljon (alapértelmezett: 3)")
    
    args = parser.parse_args()
    
    print("Eleven Labs Multi Speed Generator")
    print("=" * 60)
    
    # Ellenőrizzük, hogy a konfiguráció létezik-e
    if not Path(args.config).exists():
        print(f"Hiba: A konfigurációs fájl nem található: {args.config}")
        print("Először futtasd a keyword_config_generator.py szkriptet a konfiguráció létrehozásához.")
        sys.exit(1)
    
    # Ellenőrizzük, hogy a voice_settings.json létezik-e
    if not Path(args.voice_settings).exists():
        print(f"Hiba: A voice_settings.json fájl nem található: {args.voice_settings}")
        sys.exit(1)
    
    # Ellenőrizzük a sebesség paraméter értékét
    if args.speed < 1:
        print(f"Hiba: A sebességvariációk száma legalább 1 kell legyen, de {args.speed} lett megadva.")
        sys.exit(1)
    
    # Hang beállítások betöltése (csak az engedélyezett hangok)
    enabled_voices, full_settings = load_enabled_voices(args.voice_settings)
    print(f"{len(enabled_voices)} engedélyezett hang betöltve a voice_settings.json fájlból.")
    
    # API wrapper inicializálása
    api = ElevenLabsAPI(args.config)
    
    # API kapcsolat tesztelése
    if not api.test_api_connection():
        print("Hiba: Nem sikerült kapcsolódni az Eleven Labs API-hoz.")
        print("Ellenőrizd az API kulcsot a konfigurációs fájlban.")
        sys.exit(1)
    
    # Ellenőrizzük, hogy van-e megadva szöveg
    if args.text is None:
        print("Hiba: Nincs megadva szöveg a --text paraméterrel.")
        print("Használat: python keyword_multi_speed_script.py --text \"Generálandó szöveg\" --speed 5")
        sys.exit(1)
    
    print(f"Használt szöveg: \"{args.text}\"")
    print(f"Sebességvariációk száma: {args.speed}")
    
    # API kulcs megszerzése
    api_key = api.api_key if hasattr(api, 'api_key') else api.config.get("api_key", "")
    
    # Hangfájlok generálása az összes engedélyezett hanghoz
    for i, voice in enumerate(enabled_voices):
        try:
            # Hang paraméterek kinyerése a JSON-ból
            voice_id = voice.get("voice_id", "")
            if not voice_id:
                voice_id = voice.get("id", "")  # Régebbi formátum
                
            voice_name = voice.get("name", "Hang" + str(i + 1))
            settings = voice.get("settings", {})
            stability = settings.get("stability", 0.02)
            similarity_boost = settings.get("similarity_boost", 0.05)
            style = settings.get("style", 0.7)
            speaker_boost = settings.get("use_speaker_boost", True)
            
            print(f"\n{i + 1}. hang feldolgozása: {voice_name} (ID: {voice_id})")
            
            # Beszéd generálása különböző sebességekkel
            generate_speech_with_different_speeds(
                api_key=api_key,
                voice_id=voice_id,
                text=args.text,
                voice_name=voice_name,
                num_speeds=args.speed,
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                speaker_boost=speaker_boost
            )
        except Exception as e:
            print(f"Hiba a hang feldolgozása során: {e}")
            continue
    
    print("\nAz összes hang feldolgozása befejeződött!")
    print(f"Összesen {len(enabled_voices)} hangot dolgoztunk fel, egyenként {args.speed} sebességvariációval.")
    print(f"A generált hangfájlok száma: {len(enabled_voices) * args.speed}")

if __name__ == "__main__":
    main()

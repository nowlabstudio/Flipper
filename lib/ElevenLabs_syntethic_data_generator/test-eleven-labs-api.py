"""
Eleven Labs API Teszt Szkript

Ez a szkript teszteli az Eleven Labs API-t a konfigurációs fájl alapján.
Létrehoz egy egyszerű tesztfájlt, hogy ellenőrizze, működik-e a konfiguráció.
"""

import json
import time
import argparse
from pathlib import Path
from pydub import AudioSegment
import sys

# Eleven Labs API wrapper importálása
# Az importálási nevet igazítsuk a tényleges fájlnévhez
# Ha a fájlnév eleven-labs-api-wrapper.py:
import importlib.util
import sys
import os

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

def simple_tts_test(api, voice_id, text="cheers", output_filename=None):
    """
    Egyszerű text-to-speech teszt egy hangra.
    
    Args:
        api: Az ElevenLabsAPI példány
        voice_id: A használandó hang azonosítója
        text: A beszéddé alakítandó szöveg
        output_filename: A kimeneti fájl neve (ha None, akkor automatikusan generált)
    
    Returns:
        True, ha sikeres, False egyébként
    """
    # Hang ellenőrzése
    voice_name = api.verify_voice(voice_id)
    if not voice_name:
        print(f"Hiba: A megadott hang (ID: {voice_id}) nem található.")
        return False
    
    print(f"Hang ellenőrizve: {voice_name} (ID: {voice_id})")
    
    # Kimeneti fájlnév generálása, ha nincs megadva
    if output_filename is None:
        # A név legyen a voice_name (csak alfanumerikus karakterek) + időbélyeg
        safe_name = ''.join(c for c in voice_name if c.isalnum())
        output_filename = f"test_{safe_name}_{int(time.time())}.wav"
    
    # Kimeneti útvonal
    output_dir = Path(api.config["output"]["directory"])
    output_path = output_dir / output_filename
    
    print(f"Beszéd generálása: \"{text}\"")
    print(f"Kimeneti fájl: {output_path}")
    
    # Beszéd generálása
    temp_file = api.text_to_speech(text, voice_id, output_path)
    if not temp_file:
        print("Hiba: Nem sikerült a beszédet generálni.")
        return False
    
    print(f"Beszéd sikeresen generálva: {temp_file}")
    
    # Most teszteljük a háttérzaj generálást is
    print("\nHáttérzaj generálása tesztelése...")
    
    # Véletlenszerű zajleírás kiválasztása
    import random
    noise_types = list(api.config["background_noises"].keys())
    selected_noise = random.choice(noise_types)
    noise_desc = api.config["background_noises"][selected_noise]["sound_gen_descriptions"][0]
    
    print(f"Kiválasztott zajtípus: {selected_noise}")
    print(f"Zajleírás: \"{noise_desc}\"")
    
    # Háttérzaj generálása
    noise_bytes = api.generate_background_noise(noise_desc)
    if not noise_bytes:
        print("Figyelmeztetés: Nem sikerült háttérzajt generálni. A teszt folytatódik zaj nélkül.")
        
        # MP3 konvertálása WAV-ba
        try:
            audio = AudioSegment.from_mp3(temp_file)
            audio.export(output_path, format="wav")
            print(f"Beszéd konvertálva WAV formátumba: {output_path}")
            temp_file.unlink(missing_ok=True)  # Ideiglenes fájl törlése
            return True
        except Exception as e:
            print(f"Hiba a WAV konverzió során: {e}")
            return False
    
    print("Háttérzaj sikeresen generálva.")
    
    # Beszéd és háttérzaj keverése
    print("Beszéd és háttérzaj keverése...")
    
    try:
        # Beszéd betöltése
        speech = AudioSegment.from_mp3(temp_file)
        
        # Háttérzaj mentése ideiglenes fájlba és betöltése
        temp_bg_file = Path("temp_background.mp3")
        with open(temp_bg_file, "wb") as f:
            f.write(noise_bytes)
        
        background = AudioSegment.from_mp3(temp_bg_file)
        
        # Háttér hangerejének beállítása
        noise_volume = api.config["noise_volume"]
        background_volume_reduction = int((1 - noise_volume) * 25)
        background = background - background_volume_reduction
        
        # Háttér hosszának ellenőrzése
        if len(background) < len(speech):
            loops_needed = (len(speech) // len(background)) + 1
            background = background * loops_needed
        
        # Háttér vágása a beszéd hosszához
        background = background[:len(speech) + 1000]  # 1 másodperc ráhagyás
        
        # Beszéd és háttér keverése
        result = speech.overlay(background, position=0)
        
        # Eredmény exportálása
        result.export(output_path, format="wav")
        
        # Ideiglenes fájlok törlése
        temp_file.unlink(missing_ok=True)
        temp_bg_file.unlink(missing_ok=True)
        
        print(f"Beszéd és háttérzaj sikeresen keverve: {output_path}")
        return True
    
    except Exception as e:
        print(f"Hiba a beszéd és háttérzaj keverése során: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="Eleven Labs API tesztelő szkript")
    parser.add_argument("--config", "-c", default="config/keyword_generation_config.json", 
                        help="A konfigurációs fájl elérési útja")
    parser.add_argument("--voice", "-v", help="A tesztelendő hang azonosítója (ha nincs megadva, az első hang lesz)")
    parser.add_argument("--text", "-t", default="cheers", help="A beszéddé alakítandó szöveg")
    parser.add_argument("--output", "-o", help="A kimeneti fájl neve (opcionális)")
    
    args = parser.parse_args()
    
    print("Eleven Labs API Teszt Szkript")
    print("-" * 50)
    
    try:
        # Ellenőrizzük, hogy a pydub telepítve van-e
        import pydub
    except ImportError:
        print("Hiba: A pydub csomag nincs telepítve.")
        print("Telepítsd a következő paranccsal: pip install pydub")
        sys.exit(1)
    
    # Konfiguráció ellenőrzése
    if not Path(args.config).exists():
        print(f"Hiba: A konfigurációs fájl nem található: {args.config}")
        print("Először futtasd a keyword_config_generator.py szkriptet a konfiguráció létrehozásához.")
        sys.exit(1)
    
    # API wrapper inicializálása
    api = ElevenLabsAPI(args.config)
    
    # API kapcsolat tesztelése
    if not api.test_api_connection():
        print("Hiba: Nem sikerült kapcsolódni az Eleven Labs API-hoz.")
        print("Ellenőrizd az API kulcsot a konfigurációs fájlban.")
        sys.exit(1)
    
    # Hang kiválasztása
    voice_id = args.voice
    if not voice_id:
        # Ha nincs megadva hang, akkor az első hangot használjuk
        if api.config["voices"]:
            voice_id = api.config["voices"][0]["id"]
            print(f"Nincs megadva hang, az első hang használata: {api.config['voices'][0]['name']} (ID: {voice_id})")
        else:
            print("Hiba: Nincsenek hangok a konfigurációban.")
            sys.exit(1)
    
    # TTS teszt futtatása
    success = simple_tts_test(api, voice_id, args.text, args.output)
    
    if success:
        print("\nA teszt sikeresen lefutott! A kulcsszó-felismerés konfigurációja működik.")
    else:
        print("\nA teszt sikertelen. Ellenőrizd a hibaüzeneteket.")
        sys.exit(1)

if __name__ == "__main__":
    main()

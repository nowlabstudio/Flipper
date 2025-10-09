def fetch_voice_settings(api_key, voice_id):
    """
    Külön lekérdezi egy hang beállításait az Eleven Labs API-ról.
    Egyes hangoknál nincs settings mező, ezért szükséges lehet külön lekérdezni.
    
    Args:
        api_key: Az Eleven Labs API kulcs
        voice_id: A hang azonosítója
    
    Returns:
        A hang beállításai szótár formában, vagy alapértelmezett beállítások
    """
    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}/settings"
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            settings = response.json()
            return {
                "stability": settings.get("stability", 0.5),
                "similarity_boost": settings.get("similarity_boost", 0.75),
                "style": settings.get("style", 0.0),
                "use_speaker_boost": settings.get("use_speaker_boost", True),
                "speed": settings.get("speed", 1.0)
            }
        else:
            print(f"Figyelmeztetés: Nem sikerült lekérdezni a hang beállításait: {voice_id}")
            return {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
                "speed": 1.0
            }
    except Exception as e:
        print(f"Kivétel a hang beállításainak lekérdezése során: {e}")
        return {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
            "speed": 1.0
        }

"""
Eleven Labs Voice Fetcher

Ez a szkript lekérdezi az összes elérhető hangot az Eleven Labs API-ról és elmenti őket
egy JSON fájlba. Minden hang paraméterei között elhelyez egy "enabled" mezőt, amivel
könnyedén ki-be kapcsolhatóak az egyes hangok.
"""

import json
import requests
import argparse
import sys
from pathlib import Path

def load_api_key(config_path):
    """
    Betölti az API kulcsot a konfigurációs fájlból.
    
    Args:
        config_path: A konfigurációs fájl elérési útja
    
    Returns:
        A betöltött API kulcs
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        api_key = config.get("api", {}).get("eleven_labs_api_key", "")
        if not api_key:
            print(f"Hiba: Nem található API kulcs a konfigurációs fájlban: {config_path}")
            sys.exit(1)
        
        return api_key
    except Exception as e:
        print(f"Hiba a konfigurációs fájl betöltése során: {e}")
        sys.exit(1)

def load_existing_voice_settings(json_path):
    """
    Betölti a meglévő hang beállításokat, ha léteznek.
    
    Args:
        json_path: A JSON fájl elérési útja
    
    Returns:
        A betöltött beállítások szótár (vagy üres szótár, ha a fájl nem létezik)
    """
    try:
        if Path(json_path).exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                voice_settings = json.load(f)
                
                # Ellenőrizzük, hogy a formátum a voice_id vagy a név alapú-e
                # és alakítsuk át egy belső szótárrá, ahol a kulcs a voice_id
                voice_id_mapping = {}
                for key, data in voice_settings.items():
                    voice_id = data.get("voice_id", "")
                    if not voice_id:
                        voice_id = data.get("id", "")  # Régebbi formátum
                    
                    if voice_id:
                        voice_id_mapping[voice_id] = data
                
                return voice_id_mapping
        return {}
    except Exception as e:
        print(f"Figyelmeztetés: Nem sikerült betölteni a meglévő hang beállításokat: {e}")
        return {}

def fetch_all_voices(api_key):
    """
    Lekérdezi az összes elérhető hangot az Eleven Labs API-ról.
    
    Args:
        api_key: Az Eleven Labs API kulcs
    
    Returns:
        A hangok listája
    """
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voices_data = response.json()
            return voices_data.get("voices", [])
        else:
            print(f"Hiba a hangok lekérdezése során: {response.status_code} - {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Kivétel a hangok lekérdezése során: {e}")
        sys.exit(1)

def fetch_voice_settings(api_key, voice_id):
    """
    Lekérdezi egy hang beállításait az Eleven Labs API-ról.
    
    Args:
        api_key: Az Eleven Labs API kulcs
        voice_id: A hang azonosítója
    
    Returns:
        A hang beállításai (vagy None, ha hiba történt)
    """
    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}/settings"
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            settings = response.json()
            
            # Átalakítjuk a mezőneveket a voice_settings.json formátumára
            transformed_settings = {
                "stability": settings.get("stability", 0.5),
                "similarity_boost": settings.get("similarity_boost", 0.75),
                "style_exaggeration": settings.get("style", 0.0),
                "speaker_boost": settings.get("use_speaker_boost", True),
                "speed": 1.0  # Az API nem ad vissza sebességet, így alapértelmezett érték
            }
            
            return transformed_settings
        else:
            print(f"Figyelmeztetés: Nem sikerült lekérdezni a hang beállításait: {voice_id}")
            print(f"Válasz: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Kivétel a hang beállításainak lekérdezése során: {e}")
        return None

def update_voice_settings_json(api_key, output_file, existing_settings=None):
    """
    Frissíti a voice_settings.json fájlt az összes elérhető hanggal és beállításaikkal.
    
    Args:
        api_key: Az Eleven Labs API kulcs
        output_file: A kimeneti JSON fájl elérési útja
        existing_settings: A meglévő beállítások (ha vannak)
    
    Returns:
        Az új beállítások szótár
    """
    voices = fetch_all_voices(api_key)
    
    if not voices:
        print("Nem sikerült lekérdezni a hangokat.")
        sys.exit(1)
    
    print(f"\n{len(voices)} hang érhető el az Eleven Labs API-n:")
    print("-" * 60)
    
    # Hangok listázása
    for i, voice in enumerate(voices, 1):
        voice_id = voice.get("voice_id")
        voice_name = voice.get("name", "")
        
        # Kategória és címkék kinyerése
        category = voice.get("category", "")
        
        # Címkék kinyerése, ha léteznek
        labels = voice.get("labels", {})
        accent = labels.get("accent", "")
        age = labels.get("age", "")
        description = labels.get("description", "")
        gender = labels.get("gender", "")
        use_case = labels.get("use_case", "")
        
        # Beállítások kinyerése, ha léteznek
        settings = voice.get("settings") or {}  # Ha None, akkor üres dict
        stability = settings.get("stability", 0.5)
        similarity_boost = settings.get("similarity_boost", 0.75)
        style = settings.get("style", 0.0)
        use_speaker_boost = settings.get("use_speaker_boost", True)
        speed = settings.get("speed", 1.0)
        
        # Ellenőrizzük, hogy a hang már szerepel-e a meglévő beállításokban
        if existing_settings and voice_id in existing_settings:
            enabled_status = "Engedélyezve" if existing_settings[voice_id].get("enabled", True) else "Letiltva"
            print(f"{i}. {voice_name} (ID: {voice_id}) - Kategória: {category} - [{enabled_status}]")
            if accent:
                print(f"   Akcentus: {accent}, Nem: {gender}, Leírás: {description}")
            print(f"   Beállítások: Stability={stability}, Similarity={similarity_boost}, Speed={speed}")
        else:
            print(f"{i}. {voice_name} (ID: {voice_id}) - Kategória: {category} - [Új hang]")
            if accent:
                print(f"   Akcentus: {accent}, Nem: {gender}, Leírás: {description}")
            print(f"   Beállítások: Stability={stability}, Similarity={similarity_boost}, Speed={speed}")
    
    # Rákérdezünk a frissítésre
    while True:
        response = input("\nSzeretnéd frissíteni a voice_settings.json fájlt az összes hanggal? (igen/nem): ").strip().lower()
        if response in ["igen", "i", "yes", "y"]:
            break
        elif response in ["nem", "n", "no"]:
            print("Frissítés megszakítva.")
            return None
        else:
            print("Érvénytelen válasz. Kérlek, válaszolj 'igen' vagy 'nem'.")
    
    # Új voice_settings készítése (a kért formátumban, kulcs = hang név)
    new_voice_settings = {}
    
    # Hangok feldolgozása
    for voice in voices:
        voice_id = voice.get("voice_id")
        voice_name = voice.get("name", "")
        short_name = voice_name.split(" ")[0]  # Első szó a névből mint kulcs
        
        # Előfordul, hogy több hang is ugyanazzal a névvel kezdődik, így hozzáadjuk az ID egy részét
        if short_name in new_voice_settings:
            short_name = f"{short_name}_{voice_id[:4]}"
        
        # Kategória és címkék kinyerése
        category = voice.get("category", "")
        labels = voice.get("labels", {})
        
        # Beállítások kinyerése, ha léteznek
        settings = voice.get("settings") or {}  # Ha None, akkor üres dict
        voice_settings = {
            "stability": settings.get("stability", 0.5),
            "similarity_boost": settings.get("similarity_boost", 0.75),
            "style": settings.get("style", 0.0),
            "use_speaker_boost": settings.get("use_speaker_boost", True),
            "speed": settings.get("speed", 1.0)
        }
        
        # Ellenőrizzük, hogy létezik-e már beállítás ehhez a hanghoz
        if existing_settings and voice_id in existing_settings:
            # Meglévő beállítások kinyerése
            old_data = existing_settings[voice_id]
            enabled = old_data.get("enabled", True)
            
            # Új hang adatok összeállítása a kért formátumban
            voice_data = {
                "voice_id": voice_id,
                "name": voice_name,
                "category": category,
                "labels": labels,
                "settings": voice_settings,
                "enabled": enabled
            }
            
            # Hozzáadjuk az új beállításokhoz
            new_voice_settings[short_name] = voice_data
            
            print(f"Meglévő hangbeállítások frissítve: {voice_name} (ID: {voice_id})")
        else:
            # Új hang adatok összeállítása a kért formátumban
            voice_data = {
                "voice_id": voice_id,
                "name": voice_name,
                "category": category,
                "labels": labels,
                "settings": voice_settings,
                "enabled": True  # Alapértelmezetten engedélyezve
            }
            
            # Hozzáadjuk az új beállításokhoz
            new_voice_settings[short_name] = voice_data
            
            print(f"Új hang hozzáadva: {voice_name} (ID: {voice_id})")
    
    # Mentés JSON formátumban
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_voice_settings, f, indent=4, ensure_ascii=False)
    
    print(f"Voice beállítások sikeresen mentve: {output_file}")
    
    return new_voice_settings

def main():
    parser = argparse.ArgumentParser(description="Eleven Labs Voice Fetcher")
    parser.add_argument("--config", "-c", default="config/keyword_generation_config.json",
                        help="A konfigurációs fájl elérési útja")
    parser.add_argument("--output", "-o", default="voice_settings.json",
                        help="A kimeneti JSON fájl elérési útja")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Kihagyja a megerősítő kérdést és azonnal frissíti a JSON fájlt")
    parser.add_argument("--apikey", "-k", 
                        help="Eleven Labs API kulcs közvetlenül (opcionális)")
    
    args = parser.parse_args()
    
    print("Eleven Labs Voice Fetcher")
    print("=" * 60)
    
    # API kulcs beszerzése
    api_key = args.apikey
    
    # Ha nincs közvetlen API kulcs, próbáljuk betölteni a konfigból
    if not api_key:
        try:
            if Path(args.config).exists():
                api_key = load_api_key(args.config)
                print("API kulcs sikeresen betöltve a konfigurációs fájlból.")
            else:
                print(f"A konfigurációs fájl nem található: {args.config}")
        except Exception as e:
            print(f"Hiba a konfigurációs fájl betöltése során: {e}")
    
    # Ha még mindig nincs API kulcs, kérjük be a felhasználótól
    if not api_key:
        api_key = input("Kérlek, add meg az Eleven Labs API kulcsodat: ").strip()
        if not api_key:
            print("Nem adtál meg API kulcsot. Kilépés...")
            sys.exit(1)
    
    # Meglévő beállítások betöltése (ha vannak)
    existing_settings = load_existing_voice_settings(args.output)
    
    # Voice beállítások frissítése
    result = update_voice_settings_json(api_key, args.output, existing_settings)
    
    if result:
        print("\nA voice_settings.json fájl sikeresen frissítve.")
        print("Minden hang tartalmaz egy 'enabled' mezőt, amivel ki-be kapcsolhatók.")
        print("A JSON fájlban a hangok a rövid nevük (első szó) alapján vannak indexelve.")
        print("\nPélda a JSON formátumra:")
        print('''{
    "Rachel": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "name": "Rachel",
        "category": "professional",
        "labels": {
            "accent": "American",
            "age": "middle-aged",
            "description": "expressive",
            "gender": "female",
            "use_case": "social media"
        },
        "settings": {
            "stability": 1,
            "similarity_boost": 1,
            "style": 0,
            "use_speaker_boost": true,
            "speed": 1
        },
        "enabled": true
    },
    ...
}''')
    else:
        print("\nA voice_settings.json fájl nem lett frissítve.")

if __name__ == "__main__":
    main()

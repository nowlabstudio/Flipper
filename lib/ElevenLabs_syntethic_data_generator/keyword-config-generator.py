"""
Eleven Labs Kulcsszó-felismerés konfiguráció generátor

Ez a program egy JSON konfigurációs fájlt hoz létre az Eleven Labs API-val történő 
kulcsszó-generáláshoz szükséges alapparaméterekkel (akcentusok, zajok).
A konfigurációs fájl tartalmazza a szükséges paramétereket a dokumentum alapján,
valamint a korábban működő Python kód beállításait.
"""

import json
import os
from pathlib import Path

def create_basic_config():
    """
    Létrehoz egy alapkonfigurációt a kulcsszó-generáláshoz.
    A konfiguráció tartalmazza az akcentusokat, a beszélőket, az érzelmi variációkat,
    valamint a háttérzajokat és SNR értékeket, az Eleven Labs API-val való integrációhoz.
    """
    
    # Alapkonfiguráció definiálása
    config = {
        # API beállítások
        "api": {
            "eleven_labs_api_key": "sk_12361426642ca068e9679bea13485ee712d23a4b3bfc74e8",
            "base_url": "https://api.elevenlabs.io/v1",
            "tts_url": "https://api.elevenlabs.io/v1/text-to-speech",
            "sound_gen_url": "https://api.elevenlabs.io/v1/sound-generation",
        },
        
        # Kulcsszó és mondatok
        "keyword": {
            "main_keyword": "cheers",
            "context_examples": [
                "cheers"  # A megosztott kód alapján csak a szót használjuk
            ]
        },
        
        # Hangok beállítása az eredeti kód alapján
        "voices": [
            {
                "name": "Szilvi_US",
                "id": "uvYnpt5PleJGcyGcUYmS",
                "accent": "american"
            },
            {
                "name": "Sarah_US",
                "id": "158BdM9taSU2P9qaNQp9",
                "accent": "american"
            },
            {
                "name": "Arnold_US",
                "id": "VR6AewLTigWG4xSOukaG",
                "accent": "american"
            },
            {
                "name": "Adam_US",
                "id": "pNInz6obpgDQGcFmaJgB",
                "accent": "american"
            },
            {
                "name": "Antoni_US",
                "id": "ErXwobaYiN019PkySvjV",
                "accent": "american"
            },
            {
                "name": "Aria_US",
                "id": "9BWtsMINqrJLrRacOk9x",
                "accent": "american"
            },
            {
                "name": "Brian_US",
                "id": "nPczCjzI2devNBz1zQrb",
                "accent": "american"
            },
            {
                "name": "Dorothy_UK",
                "id": "ThT5KcBeYPX3keUQqHPh",
                "accent": "british"
            },
            {
                "name": "Elli_US",
                "id": "MF3mGyEYCl7XYWbV9V6O",
                "accent": "american"
            },
            {
                "name": "Eric_US",
                "id": "cjVigY5qzO86Huf0OWal",
                "accent": "american"
            },
            {
                "name": "Fin_FN",
                "id": "D38z5RcWu1voky8WS1ja",
                "accent": "finnish"
            },
            {
                "name": "George_UK",
                "id": "JBFqnCBsd6RMkjVDRZzb",
                "accent": "british"
            },
            {
                "name": "Joseph_UK",
                "id": "Zlb1dXrM653N07WRdFW3",
                "accent": "british"
            },
            {
                "name": "Laura_US",
                "id": "FGY2WhTYpPnrIDTdsKH5",
                "accent": "american"
            },
            {
                "name": "Lily_UK",
                "id": "pFZP5JQG7iQjIQuC4Bku",
                "accent": "british"
            },
            {
                "name": "Michael_US",
                "id": "flq6f7yk4E4fJM5XTYuZ",
                "accent": "american"
            },
            {
                "name": "Mimi_SWE",
                "id": "zrHiDhphv9ZnVXBqCLjz",
                "accent": "swedish"
            },
            {
                "name": "Patrick_US",
                "id": "ODq5zmih8GrVes37Dizd",
                "accent": "american"
            },
            {
                "name": "Rachel_US",
                "id": "21m00Tcm4TlvDq8ikWAM",
                "accent": "american"
            },
            {
                "name": "Sarah2_US",
                "id": "EXAVITQu4vr4xnSDxMaL",
                "accent": "american"
            },
            {
                "name": "Thomas_US",
                "id": "GBv7mTt0atIp3Br8iCZE",
                "accent": "american"
            },
            {
                "name": "Will_US",
                "id": "bIHbv24MWmeRgasZH58o",
                "accent": "american"
            },
            {
                "name": "Domi_US",
                "id": "AZnzlk1XvdvUeBnXmlld",
                "accent": "american"
            },
            {
                "name": "Charlotte_SWE",
                "id": "XB0fDUnXU5powFXDhCwa",
                "accent": "swedish"
            },
            {
                "name": "Callum_US",
                "id": "N2lVS1w4EtoT3dr4eOWO",
                "accent": "american"
            }
        ],
        
        # Érzelmi variációk
        "emotions": [
            {
                "name": "neutral",
                "description": "Semleges, hétköznapi kiejtés"
            },
            {
                "name": "enthusiastic",
                "description": "Lelkes, energikus kiejtés"
            }
        ],
        
        # Eleven Labs generálási paraméterek
        "generation_params": {
            "model_id": "eleven_multilingual_v2",  # Modell azonosító
            "stability": 0.5,                      # Közepes stabilitás (eredeti kódból: 0.5)
            "similarity_boost": 0.75,              # Hanghoz való hasonlóság (eredeti kódból: 0.75)
            "style": 0.0,                          # Alapértelmezett stílus (eredeti kódból: 0.0)
            "use_speaker_boost": True,             # Beszélő kiemelése bekapcsolva (eredeti kódból)
            "output_format": "mp3",                # Kimeneti formátum
            "counts_per_voice": 30,                # Generálandó fájlok száma hangoként
            "speed": {
                "values": [0.9, 1.0, 1.1],         # Lassú, normál, gyors
                "labels": ["slow", "normal", "fast"]
            }
        },
        
        # Háttérzajok - Eleven Labs Sound Generation API leírásokkal
        "background_noises": {
            "bar": {
                "description": "Bár/kávézó zajok",
                "sound_gen_descriptions": [
                    "Bar ambient noise with chatter and glasses clinking in the background"
                ]
            },
            "restaurant": {
                "description": "Éttermi zajok",
                "sound_gen_descriptions": [
                    "Restaurant ambient noise with people talking and dishes clinking"
                ]
            },
            "office": {
                "description": "Irodai háttérzajok",
                "sound_gen_descriptions": [
                    "Office background noise with typing, occasional phone rings and quiet conversations"
                ]
            },
            "cafe": {
                "description": "Kávézó környezet",
                "sound_gen_descriptions": [
                    "Cafe ambience with quiet chatter, coffee machines and soft music"
                ]
            },
            "party": {
                "description": "Parti hangulat",
                "sound_gen_descriptions": [
                    "Party ambience with music, loud talking and laughter"
                ]
            }
        },
        
        # Háttérzaj hangereje (0.0-1.0 skálán)
        "noise_volume": 0.65,
        
        # SNR (jel-zaj arány) beállítások - szimulált
        # Megjegyzés: Az Eleven Labs Sound Generation API-val generált háttérzajnál 
        # a noise_volume paraméter kontrollálja a hangerőt, nem az SNR értékek
        "snr_levels": [
            {
                "value": 15,
                "description": "Magas jel-zaj arány, a beszéd jól érthető"
            },
            {
                "value": 10,
                "description": "Közepes jel-zaj arány, a beszéd még jól érthető"
            },
            {
                "value": 5,
                "description": "Alacsony jel-zaj arány, a beszéd nehezebben érthető"
            }
        ],
        
        # Kimeneti beállítások
        "output": {
            "sample_rate": 16000,                # 16kHz mintavételezési frekvencia
            "format": "wav",                     # WAV formátum
            "directory": "generated_speech_cheers", # Kimeneti könyvtár
            "naming_pattern": "EL_{voice}_{number:02d}" # EL_hangnév_sorszám.wav
        }
    }
    
    return config

def save_config(config, filename="keyword_generation_config.json"):
    """
    Elmenti a konfigurációt JSON formátumban.
    
    Args:
        config: A konfiguráció szótár
        filename: A kimeneti fájl neve
    """
    # Biztosítjuk, hogy van kimeneti könyvtár
    output_dir = Path("config")
    output_dir.mkdir(exist_ok=True)
    
    # Teljes elérési út
    output_path = output_dir / filename
    
    # Mentés JSON formátumban, szép formázással
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print(f"Konfiguráció sikeresen mentve: {output_path}")

def main():
    """
    Fő program.
    """
    print("Eleven Labs Kulcsszó-felismerés konfiguráció generátor")
    print("-" * 60)
    
    # Konfiguráció létrehozása
    config = create_basic_config()
    
    # Konfiguráció mentése
    save_config(config)
    
    print("\nA konfiguráció megjegyzései:")
    print("1. Az API kulcs már be van állítva a megosztott szkript alapján.")
    print("2. A hangok is be vannak állítva a megosztott szkript alapján (25 hang).")
    print("3. A háttérzaj generálási leírások az Eleven Labs Sound Generation API-hoz hozzáadva.")
    print("4. A kimeneti fájl elnevezési mintája és a kimeneti könyvtár hozzáigazítva a megosztott kódhoz.")
    print("\nA konfiguráció a 'keyword_generation_tasks.md' fájl első feladatát valósítja meg,"
          "\nfelhasználva az 'elabs_cheers_with_noise.py' szkriptben található beállításokat.")

if __name__ == "__main__":
    main()

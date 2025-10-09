# ElevenLabs Szintetikus Adatgenerátor

Ez a projekt egy kulcsszó-felismerő rendszerhez készít szintetikus tréning adatokat az Eleven Labs API segítségével. A cél különböző akcentusokkal, háttérzajokkal és variációkkal rendelkező beszédhangok generálása, amelyek hatékonyan felhasználhatók egy kulcsszó-felismerő modell betanításához.

## Projektstruktúra és fájl leírások

### Fő szkriptek

| Fájl | Leírás |
|------|--------|
| `voice_fetcher_script.py` | Az Eleven Labs API-ból lekérdezi az elérhető hangokat és részletes információikat. |
| `voice-settings-collector.py` | Összegyűjti és rendszerezi a különböző hangbeállításokat, majd JSON formátumban menti azokat. |
| `voice_settings.json` | Az elérhető hangok és beállításaik tárolására szolgáló JSON fájl, amit a generálás során használunk. |
| `eleven-labs-api-wrapper.py` | Az Eleven Labs API-hoz készített egyszerű wrapper, amely megkönnyíti a hangok generálását. |
| `test-eleven-labs-api.py` | Az API kapcsolat és a generálási funkciók tesztelésére szolgáló szkript. |

### Kulcsszó generálás

| Fájl | Leírás |
|------|--------|
| `keyword-config-generator.py` | Konfigurációs fájlokat generál a kulcsszavak és variációik létrehozásához. |
| `keyword_generation_tasks.md` | A kulcsszó generálási feladatok és követelmények felsorolása és leírása. |
| `keyword_detection_prompt.md` | Részletes dokumentáció a szintetikus adatbázis felépítéséről és a generálási folyamatról. |
| `keyword_multi_speed_script.py` | Különböző beszédsebességű kulcsszó változatokat generál az Eleven Labs API-val. |

### Háttérzaj generálás és keverés

| Fájl | Leírás |
|------|--------|
| `noise_generator.py` | Környezeti háttérzajokat generál az Eleven Labs Sound Generation API segítségével különböző környezetekhez (iroda, bár, utca, otthon). Minden környezethez 10 különböző prompt áll rendelkezésre a változatosság érdekében, és minden hangfájlt 16 kHz-es mintavételezési frekvenciára konvertál. |
| `speech_noise_mixer.py` | Összekeveri a generált beszédhangokat a háttérzajokkal, változatos hangerőarányokkal. A keverés során minden fájl 16 kHz-es mintavételezési frekvenciával lesz feldolgozva és mentve. |

### Adatkönyvtárak

| Mappa | Leírás |
|-------|--------|
| `generated_speeches/` | Az Eleven Labs API-val generált tiszta beszédhangok tárolása. |
| `generated_speech_cheers/` | A "cheers" kulcsszót tartalmazó generált beszédhangok tárolása. |
| `background_noises/` | A generált környezeti háttérzajok tárolása (iroda, bár, utca, otthon). |
| `mixed_audio/` | A beszédhangok és háttérzajok keveréséből létrejött hangfájlok tárolása. |
| `config/` | Konfigurációs fájlok tárolása a generálási folyamathoz. |

## Részletes használati útmutató

### 1. Hangok és beállítások lekérése

```bash
python voice_fetcher_script.py
```

### 2. Beszéd generálása (Kulcsszó generálás)

A `keyword_multi_speed_script.py` segítségével különböző sebességű beszédhangokat generálhatunk az Eleven Labs API-n keresztül. A szkript automatikusan használja a `voice_settings.json` fájlban tárolt hangbeállításokat.

```bash
python keyword_multi_speed_script.py --text "A generálandó szöveg" --speed 3
```

#### Paraméterek:

| Paraméter | Rövidítés | Leírás | Alapértelmezett érték |
|-----------|-----------|--------|------------------------|
| `--text` | `-t` | A beszéddé alakítandó szöveg | Nincs (kötelező megadni) |
| `--speed` | `-s` | Hány különböző sebességvariációt generáljon | 3 |
| `--config` | `-c` | A konfigurációs fájl elérési útja | `config/keyword_generation_config.json` |
| `--voice_settings` | `-v` | A voice_settings.json fájl elérési útja | `voice_settings.json` |

#### Sebességbeállítások:
- A szkript a megadott számú sebességvariációt egyenletes eloszlással hozza létre a 0.7 és 1.2 közötti tartományban.
- Például ha `--speed 5`, akkor a sebességek: 0.7, 0.8, 0.9, 1.0, 1.1, 1.2 lesznek.

#### Hangbeállítások:
A `voice_settings.json` fájlban az alábbi paramétereket lehet beállítani hangoknál:
- `stability`: Befolyásolja a hang stabilitását (0.0-1.0)
- `similarity_boost`: Befolyásolja mennyire hasonlít az eredeti hangra (0.0-1.0)
- `style`: Stílus befolyásolása (0.0-1.0)
- `use_speaker_boost`: Beszélő kiemelés (true/false)
- `speed`: Beszédsebesség (a multi_speed szkript felülírja)
- `enabled`: Hang engedélyezése/letiltása (true/false)

### 3. Háttérzaj generálása

Az Eleven Labs Sound Generation API segítségével valósághű háttérzajokat generálhatunk. A szkript négy különböző környezethez tud zajokat készíteni: iroda, bár, utca és otthon.

```bash
python noise_generator.py --bar 5 --office 3 --street 4 --home 3
```

#### Paraméterek:

| Paraméter | Rövidítés | Leírás | Alapértelmezett érték |
|-----------|-----------|--------|------------------------|
| `--bar` | - | A bár környezetben generálandó zajok száma | 0 |
| `--office` | - | Az iroda környezetben generálandó zajok száma | 0 |
| `--street` | - | Az utca környezetben generálandó zajok száma | 0 |
| `--home` | - | Az otthon környezetben generálandó zajok száma | 0 |
| `--output` | `-o` | Kimeneti mappa | `background_noises` |
| `--verbose` | `-v` | Részletes kimenet, hangerő értékekkel | False |
| `--seed` | - | Random seed beállítása a reprodukálhatóságért | Nincs |

#### Egyéb tudnivalók:
- Legalább egy környezetet meg kell adni (--bar, --office, --street, --home).
- Minden környezethez 10 különböző prompt áll rendelkezésre a változatosság érdekében.
- A generált hangok 1 másodperc hosszúak és -18dB-re vannak normalizálva.
- Minden hangfájl 16 kHz-es mintavételezési frekvenciával lesz mentve WAV formátumban.
- A fájlnevek formátuma: `[környezet]_ambient_[XX].wav` (pl. `bar_ambient_01.wav`).

### 4. Beszéd és háttérzaj keverése

A `speech_noise_mixer.py` szkript a generált beszédhangfájlokat és háttérzajokat keveri össze, változatos hangerőszintekkel.

```bash
python speech_noise_mixer.py --noise-min 30 --noise-max 80
```

#### Paraméterek:

| Paraméter | Rövidítés | Leírás | Alapértelmezett érték |
|-----------|-----------|--------|------------------------|
| `--speech-dir` | - | Beszédhangokat tartalmazó mappa | `generated_speeches` |
| `--noise-dir` | - | Háttérzajokat tartalmazó mappa | `background_noises` |
| `--output-dir` | - | Kimeneti mappa | `mixed_audio` |
| `--noise-min` | - | Minimum zajhangerő százalékban | 30 |
| `--noise-max` | - | Maximum zajhangerő százalékban | 70 |
| `--seed` | - | Random seed beállítása a reprodukálhatóságért | Nincs |
| `--verbose` | `-v` | Részletes kimenet, hangerő értékekkel | False |

#### Keverési algoritmus:
1. A szkript minden beszédfájlhoz pontosan egyszer kiválaszt egy véletlenszerű háttérzajt.
2. A zajhangerő a megadott minimum és maximum érték között véletlenszerűen kerül meghatározásra.
3. A beszédhangok -20dB-re vannak normalizálva a konzisztencia érdekében.
4. A háttérzaj hangereje a beszédhez képest a megadott százalékkal állítódik be (lineáris interpolációval).
5. Minden keverék 16 kHz-es mintavételezési frekvenciával kerül mentésre.

#### Fájlnév formátum:
```
mixed_[beszédfájl neve]_[zajfájl neve]_vol[hangerő]_[időbélyeg].wav
```
Példa: `mixed_Laura_speed_0.95_bar_ambient_05_vol45_1698765432.wav`

### 5. Speech-to-Speech átalakítás (ElevenLabs API-val)

Az ElevenLabs Speech-to-Speech API segítségével meglévő hangfájlokat alakíthatunk át más hangokra. Ez a funkció Python kód használatával érhető el:

```python
import requests
import json

CHUNK_SIZE = 1024
XI_API_KEY = "<xi-api-key>"  # Az Eleven Labs API kulcsod
VOICE_ID = "<voice-id>"  # A használni kívánt hang azonosítója
AUDIO_FILE_PATH = "<path>"  # A bemeneti hangfájl elérési útja
OUTPUT_PATH = "output.mp3"  # A kimeneti hangfájl elérési útja

# Speech-to-Speech API URL
sts_url = f"https://api.elevenlabs.io/v1/speech-to-speech/{VOICE_ID}/stream"

# Fejlécek beállítása az API kéréshez
headers = {
    "Accept": "application/json",
    "xi-api-key": XI_API_KEY
}

# Adatok beállítása az API kéréshez
data = {
    "model_id": "eleven_english_sts_v2",
    "voice_settings": json.dumps({
        "stability": 0.5,
        "similarity_boost": 0.8,
        "style": 0.0,
        "use_speaker_boost": True
    })
}

# Fájl csatolása a kéréshez
files = {
    "audio": open(AUDIO_FILE_PATH, "rb")
}

# POST kérés küldése az API-nak, a válasz streamelése
response = requests.post(sts_url, headers=headers, data=data, files=files, stream=True)

# Ellenőrzés, sikeres volt-e a kérés
if response.ok:
    # Kimeneti fájl megnyitása bináris írásra
    with open(OUTPUT_PATH, "wb") as f:
        # Válasz beolvasása és írása a fájlba
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)
    print("Audio stream sikeresen mentve.")
else:
    # Hibaüzenet kiírása, ha nem sikerült a kérés
    print(response.text)
```

## Technikai részletek

- **Mintavételezési frekvencia**: Minden generált és feldolgozott hangfájl 16 kHz-es mintavételezési frekvenciát használ, ami standard a beszédfelismerő rendszerekben.
- **Normalizálás**: 
  - A háttérzajok -18dB-re vannak normalizálva a jó keverhetőség érdekében.
  - A beszédhangok a keverés során -20dB-re vannak normalizálva.
- **Variabilitás**: A rendszer több promptot használ minden környezeti zajtípushoz, és véletlenszerűen kombinálja a beszédhangokat a háttérzajokkal.
- **Fájlformátum**: Minden generált hangfájl WAV formátumban kerül mentésre.
- **Zajhangerő**: A háttérzaj hangereje a beszédhez képest százalékos arányban van megadva:
  - 0% = -50 dB (alig hallható)
  - 100% = 0 dB (ugyanolyan hangos, mint a beszéd)

## Projekt bővítési lehetőségek

- Automatizált pipeline implementálása a teljes adatgenerálási folyamathoz
- Konvolúciós keverési technikák bevezetése valószerűbb akusztikai környezetek szimulálásához
- Spektrális és időbeli augmentációs technikák alkalmazása
- Minőségellenőrzési mechanizmusok implementálása az adatkészlet validálására

## Követelmények

- Python 3.8+
- requests
- pydub
- python-dotenv
- numpy

## API Kulcs beállítása

Az Eleven Labs API kulcsot a forráskódban kell beállítani a `noise_generator.py` és egyéb fájlokban, ahol azt használjuk. 

A API kulcs megszerzéséhez:
1. Hozz létre egy fiókot az [ElevenLabs](https://elevenlabs.io/) oldalon
2. Jelentkezz be, majd a bal alsó sarokban kattints a profilképre -> "Profile + API key"
3. Kattints a szemikon ikonra a profilodhoz tartozó API kulcs megtekintéséhez
4. A kulcsot másold be a megfelelő helyekre a kódban 
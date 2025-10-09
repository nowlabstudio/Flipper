#!/usr/bin/env python3
"""
Beszéd és háttérzaj keverő szkript

Ez a szkript:
1. Minden beszédfájlhoz a 'generated_speeches' mappából
2. Véletlenszerűen kiválaszt egy háttérzaj fájlt a 'background_noises' mappából
3. Összekeveri őket állítható hangerő arányokkal, minden esetben random hangerővel
4. Az eredményt egy új mappába menti

A kimeneti fájlok száma megegyezik a beszédfájlok számával, minden beszédhang 
pontosan egyszer kerül felhasználásra, változatos háttérzaj kombinációkkal.

Minden hangfájl 16 kHz-es mintavételezési frekvenciával kerül feldolgozásra és mentésre.

Használat:
python speech_noise_mixer.py --noise-min 30 --noise-max 80
"""

import os
import sys
import argparse
import random
from pathlib import Path
from pydub import AudioSegment
import time

# Alapértelmezett beállítások
DEFAULT_SPEECH_DIR = "generated_speeches"
DEFAULT_NOISE_DIR = "background_noises"
DEFAULT_OUTPUT_DIR = "mixed_audio"
DEFAULT_NOISE_MIN = 30  # hangerő %
DEFAULT_NOISE_MAX = 90  # hangerő %
TARGET_SAMPLE_RATE = 16000  # 16 kHz

def parse_arguments():
    """Parancssori argumentumok feldolgozása"""
    parser = argparse.ArgumentParser(description='Beszéd és háttérzaj keverő')
    
    parser.add_argument('--speech-dir', type=str, default=DEFAULT_SPEECH_DIR,
                        help=f'Beszédhangokat tartalmazó mappa (alapértelmezett: {DEFAULT_SPEECH_DIR})')
    parser.add_argument('--noise-dir', type=str, default=DEFAULT_NOISE_DIR,
                        help=f'Háttérzajokat tartalmazó mappa (alapértelmezett: {DEFAULT_NOISE_DIR})')
    parser.add_argument('--output-dir', type=str, default=DEFAULT_OUTPUT_DIR,
                        help=f'Kimeneti mappa (alapértelmezett: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--noise-min', type=int, default=DEFAULT_NOISE_MIN,
                        help=f'Minimum zajhangerő százalékban (alapértelmezett: {DEFAULT_NOISE_MIN})')
    parser.add_argument('--noise-max', type=int, default=DEFAULT_NOISE_MAX,
                        help=f'Maximum zajhangerő százalékban (alapértelmezett: {DEFAULT_NOISE_MAX})')
    parser.add_argument('--seed', type=int, default=None,
                        help=f'Random seed beállítása a reprodukálhatóságért (opcionális)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Részletes kimenet, hangerő értékekkel')
    
    args = parser.parse_args()
    
    # Ellenőrizzük a hangerő értékeket
    if args.noise_min < 0 or args.noise_min > 100:
        print(f"Hiba: A minimum zajhangerő 0 és 100 között kell legyen (megadott érték: {args.noise_min})")
        sys.exit(1)
    if args.noise_max < 0 or args.noise_max > 100:
        print(f"Hiba: A maximum zajhangerő 0 és 100 között kell legyen (megadott érték: {args.noise_max})")
        sys.exit(1)
    if args.noise_min > args.noise_max:
        print(f"Hiba: A minimum zajhangerő ({args.noise_min}) nem lehet nagyobb a maximum zajhangerőnél ({args.noise_max})")
        sys.exit(1)
    
    return args

def get_audio_files(directory, extensions=['.mp3', '.wav']):
    """Adott mappából kigyűjti az audio fájlokat"""
    audio_files = []
    for file in Path(directory).glob('*'):
        if file.is_file() and file.suffix.lower() in extensions and not file.name.startswith('.'):
            audio_files.append(file)
    return audio_files

def ensure_16khz(audio_segment, source_name, verbose=False):
    """
    Biztosítja, hogy az audio 16 kHz mintavételezési frekvenciájú legyen
    
    Args:
        audio_segment: Az AudioSegment objektum
        source_name: A hang forrásának neve (debug célokra)
        verbose: Részletes kimenet engedélyezése
    
    Returns:
        Az átalakított AudioSegment
    """
    if audio_segment.frame_rate != TARGET_SAMPLE_RATE:
        if verbose:
            print(f"    {source_name} eredeti mintavételezési frekvenciája: {audio_segment.frame_rate/1000:.1f} kHz")
            print(f"    Konvertálás 16 kHz-re...")
        
        audio_segment = audio_segment.set_frame_rate(TARGET_SAMPLE_RATE)
        
        if verbose:
            print(f"    {source_name} új mintavételezési frekvenciája: {audio_segment.frame_rate/1000:.1f} kHz")
    elif verbose:
        print(f"    {source_name} mintavételezési frekvenciája már 16 kHz")
    
    return audio_segment

def mix_audio_files(speech_file, noise_file, noise_volume_percent, output_file, verbose=False):
    """
    Összekeveri a beszéd és háttérzaj fájlokat
    
    Args:
        speech_file: Beszédfájl elérési útja
        noise_file: Háttérzaj fájl elérési útja
        noise_volume_percent: Háttérzaj hangereje százalékban (0-100)
        output_file: Kimeneti fájl elérési útja
        verbose: Részletes kimenet a hangerő értékekről
    
    Returns:
        True, ha sikeres volt, False egyébként
    """
    try:
        # Beszéd betöltése
        speech_extension = speech_file.suffix.lower()
        if speech_extension == '.mp3':
            speech = AudioSegment.from_mp3(speech_file)
        elif speech_extension == '.wav':
            speech = AudioSegment.from_wav(speech_file)
        else:
            print(f"Nem támogatott beszéd fájlformátum: {speech_extension}")
            return False
        
        # Háttérzaj betöltése
        noise_extension = noise_file.suffix.lower()
        if noise_extension == '.mp3':
            noise = AudioSegment.from_mp3(noise_file)
        elif noise_extension == '.wav':
            noise = AudioSegment.from_wav(noise_file)
        else:
            print(f"Nem támogatott háttérzaj fájlformátum: {noise_extension}")
            return False
        
        # Mintavételezési frekvencia ellenőrzése és konvertálása 16 kHz-re
        speech = ensure_16khz(speech, "Beszéd", verbose)
        noise = ensure_16khz(noise, "Háttérzaj", verbose)
        
        # Háttérzaj hosszának igazítása a beszédhez
        if len(noise) < len(speech):
            # Ha a zaj rövidebb, ismételjük
            loops_needed = (len(speech) // len(noise)) + 1
            noise = noise * loops_needed
        
        # Zajt a beszéd hosszára vágjuk
        noise = noise[:len(speech)]
        
        # Eredeti beszéd hangerejének ellenőrzése
        speech_db = speech.dBFS
        noise_db = noise.dBFS
        
        if verbose:
            print(f"    Beszéd eredeti hangereje: {speech_db:.2f} dB")
            print(f"    Háttérzaj eredeti hangereje: {noise_db:.2f} dB")
        
        # Beszéd normalizálása fix értékre a konzisztencia érdekében
        target_speech_db = -20
        speech_gain_needed = target_speech_db - speech_db
        speech = speech.apply_gain(speech_gain_needed)
        
        # Háttérzaj hangerejének beállítása a beszédhez képest
        # A százalékot átalakítjuk decibel különbséggé 
        # 0% = -50 dB (alig hallható), 100% = 0 dB (ugyanolyan hangos, mint a beszéd)
        min_db_diff = -30  # legcsendesebb
        max_db_diff = +10    # leghangosabb
        
        # Lineáris interpoláció a megadott százalék alapján
        noise_db_diff = min_db_diff + (noise_volume_percent / 100.0) * (max_db_diff - min_db_diff)
        
        # A zajnak a beszédhez képest noise_db_diff-el hangosabbnak vagy csendesebbnek kell lennie
        target_noise_db = target_speech_db + noise_db_diff
        noise_gain_needed = target_noise_db - noise_db
        noise = noise.apply_gain(noise_gain_needed)
        
        if verbose:
            print(f"    Beszéd normalizált hangereje: {speech.dBFS:.2f} dB")
            print(f"    Háttérzaj beállított hangereje: {noise.dBFS:.2f} dB")
            print(f"    Hangerő különbség: {noise_db_diff:.2f} dB ({noise_volume_percent}%)")
        
        # Hangok keverése
        mixed = speech.overlay(noise)
        
        # Ellenőrizzük a végső hangfájl mintavételezési frekvenciáját
        if verbose:
            print(f"    Végső hangfájl mintavételezési frekvenciája: {mixed.frame_rate/1000:.1f} kHz")
        
        # Eredmény mentése
        mixed.export(output_file, format="wav")
        
        return True
    except Exception as e:
        print(f"Hiba a hangok keverése során: {e}")
        return False

def main():
    print("Beszéd és háttérzaj keverő")
    print("==========================")
    
    # Argumentumok feldolgozása
    args = parse_arguments()
    
    # Random seed beállítása ha meg van adva
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Random seed beállítva: {args.seed}")
    else:
        # Egyébként időalapú véletlenszerűség
        random.seed(int(time.time()))
    
    # Mappák ellenőrzése
    speech_dir = Path(args.speech_dir)
    noise_dir = Path(args.noise_dir)
    output_dir = Path(args.output_dir)
    
    if not speech_dir.exists() or not speech_dir.is_dir():
        print(f"Hiba: A megadott beszéd mappa nem létezik: {speech_dir}")
        sys.exit(1)
    
    if not noise_dir.exists() or not noise_dir.is_dir():
        print(f"Hiba: A megadott háttérzaj mappa nem létezik: {noise_dir}")
        sys.exit(1)
    
    # Kimeneti mappa létrehozása
    output_dir.mkdir(exist_ok=True)
    
    # Audio fájlok összegyűjtése
    speech_files = get_audio_files(speech_dir)
    noise_files = get_audio_files(noise_dir)
    
    if not speech_files:
        print(f"Hiba: Nem találhatók beszédfájlok a megadott mappában: {speech_dir}")
        sys.exit(1)
    
    if not noise_files:
        print(f"Hiba: Nem találhatók háttérzaj fájlok a megadott mappában: {noise_dir}")
        sys.exit(1)
    
    print(f"Talált beszédfájlok: {len(speech_files)}")
    print(f"Talált háttérzaj fájlok: {len(noise_files)}")
    print(f"Létrehozandó keverékek száma: {len(speech_files)}")
    
    # Véletlenszerűen megkeverjük a beszédfájlok és zajfájlok sorrendjét
    # Ez segít biztosítani, hogy a kombinációk változatosak legyenek
    random.shuffle(speech_files)
    
    # Létrehozunk egy listát a zajfájlokból, amit fel fogunk használni
    # Ha kevesebb zajfájl van, mint beszédfájl, akkor ismétlünk, de véletlenszerűen
    noise_selection = []
    while len(noise_selection) < len(speech_files):
        # Megkeverjük a zajfájlokat és hozzáadjuk a választási listához
        random.shuffle(noise_files)
        noise_selection.extend(noise_files)
    
    # Csak annyi zajfájlt használunk, amennyire szükség van
    noise_selection = noise_selection[:len(speech_files)]
    
    # Keverékek generálása
    successful = 0
    timestamp = int(time.time())
    
    # Megnézzük, hogy milyen kombinációkat fogunk használni
    combinations = []
    for speech_file, noise_file in zip(speech_files, noise_selection):
        combinations.append((speech_file.name, noise_file.name))
    
    # Kiírjuk az összes lehetséges és a kiválasztott kombinációk számát
    total_possible_combinations = len(speech_files) * len(noise_files)
    print(f"\nLehetséges kombinációk száma: {total_possible_combinations}")
    print(f"Kiválasztott kombinációk száma: {len(combinations)}")
    print(f"Mintavételezési frekvencia: {TARGET_SAMPLE_RATE/1000:.1f} kHz")
    
    # Generáljuk a keverékeket
    for i, (speech_file, noise_file) in enumerate(zip(speech_files, noise_selection)):
        # Véletlenszerű zajhangerő a megadott tartományban
        # Az értékeket precíz lebegőpontos számként határozzuk meg a jobb variabilitásért
        noise_volume = random.uniform(args.noise_min, args.noise_max)
        noise_volume = round(noise_volume, 1)  # Egy tizedes pontosság
        
        # Fájlnevek kinyerése az eredeti fájlokból
        speech_name = speech_file.stem
        noise_name = noise_file.stem
        
        # Kimeneti fájlnév generálása
        output_file = output_dir / f"{speech_name}_{noise_name}_vol{noise_volume:.1f}_{timestamp}_{i:02d}_noise.wav"
        
        print(f"\nKeverék {i+1}/{len(speech_files)} generálása:")
        print(f"  Beszéd: {speech_file.name}")
        print(f"  Háttérzaj: {noise_file.name}")
        print(f"  Zajhangerő: {noise_volume:.1f}%")
        
        # Hangok keverése
        if mix_audio_files(speech_file, noise_file, noise_volume, output_file, args.verbose):
            print(f"  Sikeres keverés! Mentve: {output_file.name}")
            successful += 1
        else:
            print(f"  Hiba történt a keverés során!")
    
    # Statisztika kiírása
    print("\nÖsszesítés:")
    print(f"- Sikeres keverések: {successful}/{len(speech_files)}")
    print(f"- Zajhangerő tartománya: {args.noise_min}% - {args.noise_max}%")
    print(f"- Kimeneti mappa: {output_dir}")
    print(f"- Mintavételezési frekvencia: 16 kHz")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Háttérzaj generáló szkript

Ez a szkript az Eleven Labs Sound Generation API-t használja különböző
realisztikus környezeti zajok generálására, amelyek később összekeverhetők a beszédhangokkal.

A generált zajok öt környezethez készülnek:
1. Iroda (--office)
2. Bár (--bar)
3. Utca (--street)
4. Otthon (--home)
5. Beszéd (--speech)

Minden flag után opcionálisan megadható egy szám, ami meghatározza, hány variánst generáljon:
python noise_generator.py --bar 5 --office 3 --speech 4

A hangfájlok 1000ms (1 másodperc) hosszúak és WAV formátumban kerülnek mentésre.
Az Eleven Labs által generált hangok 16 kHz mintavételezési frekvenciára lesznek konvertálva.

Minden környezethez 10 különböző prompt áll rendelkezésre, amelyek segítenek változatos zajokat generálni.
"""

import os
import sys
import time
import requests
import json
import argparse
import random
from pathlib import Path
from pydub import AudioSegment

# API Kulcs - helyettesítse a sajátjával
API_KEY = "sk_12361426642ca068e9679bea13485ee712d23a4b3bfc74e8"

# Részletes zajleírások az egyes környezetekhez - minden környezethez 10 különböző prompt
NOISE_DESCRIPTIONS = {
    "office": [
        "High-quality office ambience. Professional environment with distant keyboard typing, subtle mouse clicks, gentle paper shuffling, muffled conversations in the background, occasional office chair movement, and quiet HVAC system running. The sound is clean, realistic, and has excellent spatial characteristics. The sound should last for exactly 1 second.",
        
        "Busy office environment with multiple people typing on keyboards, conference call in a nearby meeting room, printer operating in the background, coffee machine brewing, and occasional office chatter. Clear and immersive sound quality with realistic spatial positioning. The sound should last for exactly 1 second.",
        
        "Morning office atmosphere with fewer people, quiet conversations, gentle keyboard typing, phone ringing in the distance, papers being organized, and the subtle hum of computers starting up. The sound has natural reverb of an office space with high ceilings. The sound should last for exactly 1 second.",
        
        "Corporate office environment with air conditioning system, elevator bell in the distance, footsteps on carpet, quiet discussion about business matters, typing on mechanical keyboards, and occasional desk drawer opening and closing. The sound should last for exactly 1 second.",
        
        "Open-plan office with background hum of fluorescent lights, multiple conversations at varying distances, mouse clicks, keyboard typing with different intensities, desk phone ringing briefly, and someone using a stapler. Clear stereo imaging with excellent depth perception. The sound should last for exactly 1 second.",
        
        "Late evening office ambience with fewer people, occasional typing, subtle chair movements, someone packing up to leave, distant printer finishing a job, and the building's ventilation system becoming more noticeable in the quiet. The sound should last for exactly 1 second.",
        
        "Office kitchen area with coffee machine brewing, microwave running, refrigerator humming, utensils being taken from drawers, quiet conversations about non-work topics, and water being poured into a cup. Realistic spatial audio with clearly defined sound sources. The sound should last for exactly 1 second.",
        
        "Office lobby with receptionist typing at computer, automatic doors opening and closing, footsteps on marble floor, visitor signing in, elevator arriving with a ding, and distant office sounds. The sound should last for exactly 1 second.",
        
        "Tech startup office with energetic atmosphere, multiple keyboards with mechanical switches being typed on, casual conversations about coding, desk fan running, someone adjusting their standing desk, and app notification sounds from various devices. The sound should last for exactly 1 second.",
        
        "Traditional office with older equipment, dot matrix printer operating, landline phones ringing, filing cabinet drawers opening and closing, analog clock ticking, older computer fans running louder, and formal business conversations. The sound should last for exactly 1 second."
    ],
    
    "bar": [
        "High-quality bar ambience. Lively but not overwhelming environment with distinct glass clinking, murmured conversations creating a warm atmosphere, occasional laughter, subtle background music, and bartender mixing drinks. The sound is immersive, balanced, and captures natural reverb of the space. The sound should last for exactly 1 second.",
        
        "Busy Friday night bar atmosphere with louder conversations, frequent laughter, glasses clinking, cash register opening and closing, ice being scooped, bartender shaking cocktails, and upbeat music playing at moderate volume. The sound should last for exactly 1 second.",
        
        "Cozy neighborhood pub with quiet jazz music, fewer patrons having more intimate conversations, occasional pool ball clacking, beer being poured from tap, glass being placed on wooden counter, and subtle creaking of wooden bar stools. The sound should last for exactly 1 second.",
        
        "Sports bar during game night with excited reactions from patrons, television commentary faintly audible, glasses and bottles clinking in celebration, servers moving between tables, bar stools moving, and occasional cheering. The sound should last for exactly 1 second.",
        
        "Upscale cocktail bar with sophisticated atmosphere, quiet elegant music, ice clinking in premium glassware, professional bartenders using cocktail shakers, subtle conversations about business and arts, and the sound of expensive liquor being poured. The sound should last for exactly 1 second.",
        
        "College bar with energetic younger crowd, louder pop music, multiple simultaneous conversations, frequent laughter, drink orders being shouted, bottles opening, and bar games being played in the background. The sound should last for exactly 1 second.",
        
        "Wine bar with relaxed ambience, cork being removed from bottle, wine being poured into glasses, knowledgeable conversations about vintages, cheese board being served on marble surface, and classical music playing softly. The sound should last for exactly 1 second.",
        
        "Dive bar with jukebox playing classic rock, fewer but more boisterous patrons, occasional sound of beer bottles opening, peanut shells being cracked, older wood furniture creaking, and raspy laughter. The sound should last for exactly 1 second.",
        
        "Hotel lobby bar with international travelers, rolling luggage passing by, multi-language conversations, cocktail being mixed, hotel staff greeting guests, and light hotel lobby jazz playing in the background. The sound should last for exactly 1 second.",
        
        "Bar at closing time with fewer customers, chairs being moved as cleaning begins, last call being announced, bills being settled, glasses being collected, and music volume being lowered as the night winds down. The sound should last for exactly 1 second."
    ],
    
    "street": [
        "High-quality urban street ambience. Moderately busy city street with passing cars at medium distance, footsteps on pavement, distant honking, subtle wind through buildings, occasional door opening, and indistinct urban chatter. The sound has excellent stereo imaging and depth, with clear foreground and background elements. The sound should last for exactly 1 second.",
        
        "Downtown city street during rush hour with frequent car horns, heavier traffic passing, bus braking and doors opening, multiple conversations as pedestrians walk by, construction sounds in the distance, and city pigeons fluttering. The sound should last for exactly 1 second.",
        
        "Quiet residential street with occasional car passing slowly, birds chirping, distant children playing, dog barking from inside a home, leaves rustling in light breeze, and mail carrier's footsteps approaching. The sound should last for exactly 1 second.",
        
        "Busy pedestrian shopping street with no vehicles, multiple conversations as people walk by, shopping bags rustling, store door opening with bell chiming, street performer in the distance, and sound of outdoor café dishes clinking. The sound should last for exactly 1 second.",
        
        "Main avenue during light rain with car tires on wet pavement, raindrops on store awnings, people hurrying with umbrellas opening, windshield wipers functioning, and reduced street chatter as people seek shelter. The sound should last for exactly 1 second.",
        
        "Night-time urban street with reduced traffic, distant bass from a nightclub, group of people leaving restaurant, taxi pulling up to curb, police siren very far away, and footsteps echoing more distinctly. The sound should last for exactly 1 second.",
        
        "Street market with vendors calling out, customers negotiating, bags being filled with produce, cash transactions, children excited by street food, and general bustling commerce atmosphere. The sound should last for exactly 1 second.",
        
        "Street intersection with traffic signal, cars stopping and starting, pedestrian crossing signal beeping, group waiting to cross talking amongst themselves, bicycle bell as cyclist navigates through, and idling engine sounds. The sound should last for exactly 1 second.",
        
        "Narrow European street with echoing footsteps between buildings, vespa or scooter passing by, church bells in the distance, café chairs moving on cobblestone, conversation in another language, and street cleaning vehicle approaching. The sound should last for exactly 1 second.",
        
        "Urban street during festival or event with more crowded sidewalks, excited conversations, street food being prepared, temporary speaker playing music, children laughing, and periodic crowd reactions to street performances. The sound should last for exactly 1 second."
    ],
    
    "home": [
        "High-quality home ambience. Cozy interior with subtle refrigerator hum, distant TV sounds at low volume, occasional creaking of furniture, soft footsteps on wooden floor, gentle rustling from air conditioning or heating, and muted outdoor sounds through closed windows. The sound is warm, natural and creates a comfortable acoustic space. The sound should last for exactly 1 second.",
        
        "Active family home with children playing in another room, kitchen activities with water running and dishwasher operating, dog moving across hardwood floor, laundry machine in mid-cycle, and casual family conversation in the background. The sound should last for exactly 1 second.",
        
        "Evening home atmosphere with quieter setting, book page turning, tea kettle beginning to heat, wall clock ticking, cat purring, subtle phone notification, and distant neighbor activity barely audible. The sound should last for exactly 1 second.",
        
        "Weekend morning home ambience with coffee brewing, newspaper pages rustling, toast popping up from toaster, morning news on TV at low volume, shower running in the bathroom, and birds audible through slightly open window. The sound should last for exactly 1 second.",
        
        "Home during rainfall with rain hitting windows, roof and gutters, increased indoor coziness, tea being stirred in cup, blanket being adjusted on couch, and a cooking timer going off in the kitchen. The sound should last for exactly 1 second.",
        
        "Home office setting with computer keyboard typing, mouse clicking, desk chair adjusting, paper documents being organized, coffee cup being placed on desk, and house settling noises in the background. The sound should last for exactly 1 second.",
        
        "Evening dinner time at home with plates and utensils, serving dishes being placed on table, glasses being filled, chairs moving as family sits down, casual dinner conversation starting, and kitchen appliance running in background. The sound should last for exactly 1 second.",
        
        "Late night home ambience with nearly everything quiet, distant street traffic occasionally passing, refrigerator cycling on, digital clock display changing with subtle electronic sound, floorboards subtly settling, and very faint ticking of house utilities. The sound should last for exactly 1 second.",
        
        "Home with open windows during spring/summer with increased outdoor sounds, ceiling fan rotating, ice shifting in freezer, curtains moving with breeze, wind chimes from porch or garden, and distant lawn mower. The sound should last for exactly 1 second.",
        
        "Multi-story home with unique spatial characteristics, sounds from floor above with subtle footsteps, water flowing through pipes in walls, HVAC system starting cycle, garage door operating in distance, and home security system subtle operational noises. The sound should last for exactly 1 second."
    ],
    
    "speech": [
        "High-quality background speech ambience with multiple conversations occurring simultaneously at varying distances. There should be no distinguishable words, just the acoustic patterns of human speech with different tones, pitches, and rhythms creating a natural speech bubble effect. The conversations should sound authentic but unintelligible, with occasional laughter and vocal inflections. The sound should last for exactly 1 second.",
        
        "Conference room speech ambience with professional conversation tones. Multiple people speaking with measured, business-like cadence at medium distances from the listener. The speech should sound like a meeting in progress with occasional agreement sounds, paper shuffling, and one person speaking slightly louder as if presenting. No distinguishable words, just the sound texture of professional speech. The sound should last for exactly 1 second.",
        
        "Restaurant dining speech ambience with relaxed conversations happening across multiple tables. The speech should include the musical qualities of dining conversation - higher female voices, deeper male voices, occasional child voices, soft laughter, and the rhythm of eating pauses. No distinguishable words, just the warm acoustic pattern of people enjoying meals together. The sound should last for exactly 1 second.",
        
        "Classroom or lecture speech ambience with one primary speaker at medium distance and occasional quieter responses from an audience. The speech pattern should resemble educational cadence with explaining tones, question intonations, and brief moments of note-taking quiet. No words should be understandable, just the sonic texture of learning environment speech. The sound should last for exactly 1 second.",
        
        "International airport terminal speech ambience with multiple languages being spoken simultaneously. The speech should include various linguistic rhythms and tones, occasional announcement-like cadences in the background, and the distinct sound of travelers conversing with varying urgency levels. No distinguishable words, just the rich acoustic tapestry of global speech patterns. The sound should last for exactly 1 second.",
        
        "Social gathering speech ambience with animated friendly conversation, featuring multiple people speaking with enthusiasm. The speech should include the acoustic features of storytelling, reactive sounds, warm laughter, and the rising/falling patterns of engaged social interaction. No distinguishable words, just the lively sonic texture of people enjoying conversation. The sound should last for exactly 1 second.",
        
        "Medical waiting room speech ambience with quieter, more reserved conversation tones. The speech should feature the subdued acoustic pattern of people speaking in semi-private tones, occasional whispers, pages turning, and the measured rhythm of professional-to-patient conversation in the background. No distinguishable words, just the careful speech texture of a health environment. The sound should last for exactly 1 second.",
        
        "University campus outdoor speech ambience with younger adult voices in a scholarly environment. The speech should include the energetic patterns of academic discussion, passing greetings, multiple conversation groups forming and dissolving, and the particular rhythm of walking-while-talking. No distinguishable words, just the dynamic sonic signature of campus speech. The sound should last for exactly 1 second.",
        
        "Shopping mall speech ambience with consumer-environment conversation patterns. The speech should feature the distinct acoustic signature of customer-to-staff interactions, family shopping discussions, scattered questions and responses, and the particular rhythm of browsing-while-talking. No distinguishable words, just the characteristic sound texture of retail speech. The sound should last for exactly 1 second.",
        
        "Train or public transit speech ambience with the particular acoustic properties of commuter conversations. The speech should include the start-stop rhythm of movement-affected talking, announcement-style cadences in the background, brief exchanges between strangers, and the spatial audio signature of conversations in a moving vehicle with varied distances. No distinguishable words, just the unique sound pattern of transit speech. The sound should last for exactly 1 second."
    ]
}

# Kimeneti könyvtár
OUTPUT_DIR = "background_noises"

# API végpont
SOUND_GEN_URL = "https://api.elevenlabs.io/v1/sound-generation"

def generate_background_noise(description):
    """
    Háttérzaj generálása az Eleven Labs Sound Generation API-val
    
    Args:
        description: A generálandó zaj részletes szöveges leírása
        
    Returns:
        Az audio bájtok vagy None, ha hiba történt
    """
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "text": description
    }
    
    try:
        print(f"Háttérzaj generálása...")
        response = requests.post(
            SOUND_GEN_URL,
            json=data,
            headers=headers
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

def save_noise(noise_bytes, noise_type, output_dir, variant_num=None):
    """
    Elmenti a generált zajt
    
    Args:
        noise_bytes: A zaj bájtok
        noise_type: A zaj típusa (pl. "office", "bar")
        output_dir: A kimeneti könyvtár elérési útja
        variant_num: Variáns száma (opcionális)
    """
    # Ideiglenes fájl létrehozása
    temp_file = Path(output_dir) / "temp_noise.mp3"
    with open(temp_file, "wb") as f:
        f.write(noise_bytes)
    
    # Audio betöltése
    try:
        noise = AudioSegment.from_mp3(temp_file)
        
        # Az eredeti mintavételezési frekvencia ellenőrzése és kiírása
        original_frame_rate = noise.frame_rate
        print(f"    Eredeti mintavételezési frekvencia: {original_frame_rate/1000:.1f} kHz")
        
        # Konvertálás 16 kHz-re
        target_frame_rate = 16000
        if original_frame_rate != target_frame_rate:
            noise = noise.set_frame_rate(target_frame_rate)
            print(f"    Konvertálva 16 kHz-re")
        
        # Hossz korrigálása pontosan 1000ms-ra
        if len(noise) > 1000:
            noise = noise[:1000]
        elif len(noise) < 1000:
            # Ha rövidebb, ismételjük addig, amíg eléri az 1000ms-t
            while len(noise) < 1000:
                noise += noise
            noise = noise[:1000]
        
        # Normalizálás -18dB-re a jobb keverhetőség érdekében
        target_dBFS = -18.0
        change_in_dBFS = target_dBFS - noise.dBFS
        normalized_noise = noise.apply_gain(change_in_dBFS)
        
        # Ellenőrzés, hogy a mintavételezési frekvencia biztosan 16 kHz
        print(f"    Végső mintavételezési frekvencia: {normalized_noise.frame_rate/1000:.1f} kHz")
        
        # Fájlnév meghatározása
        if variant_num is not None:
            output_file = Path(output_dir) / f"{noise_type}_ambient_{variant_num:02d}.wav"
        else:
            output_file = Path(output_dir) / f"{noise_type}_ambient.wav"
            
        # Mentés wav formátumban
        normalized_noise.export(output_file, format="wav")
        print(f"Mentve: {output_file}")
        
        # Ideiglenes fájl törlése
        temp_file.unlink(missing_ok=True)
        
        return True
    except Exception as e:
        print(f"Hiba a zaj feldolgozása során: {e}")
        if temp_file.exists():
            temp_file.unlink(missing_ok=True)
        return False

def select_description(env_type, index):
    """
    Kiválasztja a megfelelő leírást az adott környezethez és variáns indexhez
    
    Args:
        env_type: Környezet típusa (pl. "bar")
        index: A variáns indexe (0-tól kezdődően)
        
    Returns:
        A kiválasztott leírás
    """
    if env_type not in NOISE_DESCRIPTIONS:
        print(f"Hiba: Ismeretlen környezet típus: {env_type}")
        return None
    
    # Az index-edik leírást választjuk, de ha túl magas az index,
    # akkor az első 10 leírás között választunk ciklikusan
    descriptions = NOISE_DESCRIPTIONS[env_type]
    if index < len(descriptions):
        selected_description = descriptions[index]
    else:
        # Ha túl sok variánst kértek (10-nél többet), akkor az első leírásokat használjuk újra
        selected_description = descriptions[index % len(descriptions)]
    
    return selected_description

def generate_variants_for_environment(env_type, count, output_dir):
    """
    Generál megadott számú zajvariánst egy környezethez
    
    Args:
        env_type: Környezet típusa (pl. "bar")
        count: Generálandó variánsok száma
        output_dir: Kimeneti könyvtár
        
    Returns:
        Sikeres generálások száma
    """
    if env_type not in NOISE_DESCRIPTIONS:
        print(f"Hiba: Ismeretlen környezet típus: {env_type}")
        return 0
        
    successful = 0
    
    print(f"\n--- {env_type.upper()} környezet: {count} variáns generálása ---")
    print(f"Rendelkezésre álló promptok száma: {len(NOISE_DESCRIPTIONS[env_type])}")
    
    for i in range(count):
        # Megfelelő leírás kiválasztása az i. variánshoz
        description = select_description(env_type, i)
        
        if not description:
            continue
        
        print(f"Variáns {i+1}/{count} generálása...")
        print(f"Használt prompt: \"{description[:70]}...\"")
        
        # Zaj generálása
        noise_bytes = generate_background_noise(description)
        
        if noise_bytes:
            # Zaj mentése
            if save_noise(noise_bytes, env_type, output_dir, i+1 if count > 1 else None):
                successful += 1
        
        # Ratelimit elkerülése
        time.sleep(2)
    
    return successful

def parse_arguments():
    """Parancssori argumentumok feldolgozása"""
    parser = argparse.ArgumentParser(description='Háttérzaj generáló eszköz')
    
    parser.add_argument('--office', type=int, nargs='?', const=1, 
                        help='Irodai zaj generálása (opcionálisan megadható a variánsok száma)')
    parser.add_argument('--bar', type=int, nargs='?', const=1, 
                        help='Bár zaj generálása (opcionálisan megadható a variánsok száma)')
    parser.add_argument('--street', type=int, nargs='?', const=1, 
                        help='Utcai zaj generálása (opcionálisan megadható a variánsok száma)')
    parser.add_argument('--home', type=int, nargs='?', const=1, 
                        help='Otthoni zaj generálása (opcionálisan megadható a variánsok száma)')
    parser.add_argument('--speech', type=int, nargs='?', const=1, 
                        help='Beszéd háttérzaj generálása (opcionálisan megadható a variánsok száma)')
    parser.add_argument('--output', '-o', type=str, default=OUTPUT_DIR,
                        help=f'Kimeneti könyvtár (alapértelmezett: {OUTPUT_DIR})')
    
    args = parser.parse_args()
    
    # Ellenőrizzük, hogy legalább egy környezet meg van-e adva
    if not any([args.office, args.bar, args.street, args.home, args.speech]):
        parser.print_help()
        print("\nFigyelmeztetés: Nincs megadva generálandó környezet.")
        print("Használja a --office, --bar, --street, --home vagy --speech flageket a zajok generálásához.")
        print("Példa: python noise_generator.py --bar 5 --office 3 --speech 4")
        sys.exit(1)
        
    return args

def main():
    print("Háttérzaj generáló eszköz")
    print("========================")
    
    # Argumentumok feldolgozása
    args = parse_arguments()
    
    # Beállítások ellenőrzése
    if not API_KEY.startswith("sk_"):
        print("Hiba: Érvénytelen API kulcs. Kérem, állítson be egy érvényes Eleven Labs API kulcsot.")
        sys.exit(1)
    
    # Kimeneti könyvtár létrehozása
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    print(f"Kimeneti könyvtár: {output_dir}")
    
    # Környezetek feldolgozása
    env_counts = {
        "office": args.office,
        "bar": args.bar,
        "street": args.street,
        "home": args.home,
        "speech": args.speech
    }
    
    success_count = 0
    total_variants = 0
    
    # Csak azokat a környezeteket generáljuk, amelyeket a felhasználó kért
    for env_type, count in env_counts.items():
        if count:
            success = generate_variants_for_environment(env_type, count, output_dir)
            success_count += 1 if success > 0 else 0
            total_variants += success
    
    # Statisztika kiírása
    print("\nÖsszesítés:")
    print(f"- Feldolgozott környezetek: {success_count}/{sum(1 for c in env_counts.values() if c)}")
    print(f"- Összes generált variáns: {total_variants}")
    print(f"- Kimeneti könyvtár: {output_dir}")
    
    # Használati útmutató
    print("\nHasználati útmutató:")
    print("1. A generált zajfájlok 1 másodperc hosszúak")
    print("2. A fájlok -18dB-re normalizáltak a jó keverhetőség érdekében")
    print("3. A zajok használhatók a beszédhangokkal való összekeverésre")
    print("4. Minden környezethez 10 különböző prompt áll rendelkezésre a változatosságért")
    print("5. A generált hangok mintavételezési frekvenciája 16 kHz")

if __name__ == "__main__":
    main()
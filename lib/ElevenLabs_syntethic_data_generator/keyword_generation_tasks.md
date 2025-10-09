# Kulcsszó ("Cheers") generálás egyszerűsített feladatlistája

## 1. Előkészítés és API integráció

- [x] Egyszerű JSON konfiguráció létrehozása az alapparaméterekhez (akcentusok, zajok)
- [x] Eleven Labs API alap wrapper implementálása (autentikáció és egyszerű hívások)
- [x] API kulcs és hozzáférések beállítása

## 2. Kulcsszó variációk

- [x] 5-6 fő akcentus kiválasztása (amerikai, brit, francia, német, svéd, indiai)
- [x] Akcentusonként 2-3 különböző hang (férfi/női) kiválasztása
- [x] Alap érzelmi variációk: semleges, lelkes (2 variáció)

## 3. Eleven Labs generálás

- [x] Egyszerű generálási szkript a kiválasztott hangokhoz
- [x] Generálási paraméterek: közepes stability/clarity értékek
- [x] Kulcsszavak batch-generálása és tárolása

## 4. Hangfeldolgozás

- [ ] Alapvető minőségellenőrzés (csak a hibás generációk kiszűrése)
- [ ] Hangerő normalizálás
- [ ] Egységes fájlformátum és mintavételezési frekvencia (16kHz)

## 5. Háttérzaj hozzáadása

- [ ] 3-4 alap környezeti zaj beszerzése (iroda, bár, utca, otthon)
- [ ] Egyszerű zajkeverés 3 SNR szinttel (15dB, 10dB, 5dB)
- [ ] Zajjal kevert fájlok mentése Edge Impulse kompatibilis formátumban
# Szintetikus adatbázis tervezés és megvalósítás kulcsszó-felismeréshez

## 1. Szintetikus adatbázis tervezés kulcsszó-felismeréshez

### 1.1 Kulcsszó-generálás különböző akcentusokkal (Eleven Labs segítségével)

- **Akcentusok kiválasztása**: Angol nyelv főbb regionális változatai (amerikai, brit, ausztrál, kanadai) mellett francia, német, svéd, olasz, spanyol, japán, kínai, indiai akcentusok
- **Beszélők variabilitása**: Minden akcentushoz legalább 3-5 különböző beszélő (férfi, női, különböző életkorú)
- **Eleven Labs beállítások**:
  - Stabilitás: Közepesre állítva, hogy természetes változatosságot adjon, de felismerhető maradjon
  - Beszédsebesség variációk: Lassú, normál és gyors tempójú kiejtések minden akcentushoz
  - Hangerő és hangsúlyozás: Változatos hangsúlyminták a kulcsszón

### 1.2 Kulcsszavak módosítása és háttérzajok integrálása

- **SNR skálázás**: Különböző jel-zaj arányok beállítása (20dB, 15dB, 10dB, 5dB, 0dB)
- **Háttérzaj típusok és források**:
  - Iroda: Billentyűzet kopogás, nyomtató, beszélgetésfoszlányok, légkondicionáló
  - Bár/kávézó: Pohárcsörgés, háttérzene, beszélgetés moraja
  - Utcai forgalom: Járművek, szél, távolabb beszélő emberek
  - Otthoni környezet: Háztartási gépek, TV/rádió háttérben
- **Pozicionálás variációk**: A hangforrás távolságának szimulálása (közeli, közepes, távoli)

### 1.3 Dialektusok és kiejtési variációk gazdagítása

- **Természetes variációk**: Különböző hangsúlyozási minták ugyanazon akcentuson belül
- **Adataugmentáció**: Pitch shifting és időbeli nyújtás/zsugorítás technikákkal a mintaszám növelése
- **Kontextuális variációk**: A "cheers" különböző használati kontextusokban (koccintás, elköszönés)
- **Érzelmi variációk**: Lelkes, hétköznapi, visszafogott kiejtések

### 1.4 Ismeretlen szavak gyűjteményének létrehozása

- **Fonetikai hasonlóság alapján**:
  - Közeli szavak: "cheese", "cheetah", "cheeks", "cheat", "cheer" (egyes számban)
  - Hasonló fonémák: "fears", "tears", "gears", "beers", "peers"
  - Hasonló szótagszerkezet: "sneers", "jeers", "clears", "nears", "years"
- **Eleven Labs generálás**: Ugyanazon akcentusokkal és beszélőkkel, mint a kulcsszónál
- **Természetes beszédrészletek**: Mindennapi társalgások rövid részletei, amelyek nem tartalmazzák a kulcsszót
- **Számok és parancsszavak**: A rendszerben potenciálisan előforduló egyéb parancsok

### 1.5 Neutrális zajok gyűjteménye

- **Tiszta háttérzajok**: A különböző környezetekből tiszta zajminták, beszéd nélkül
- **Zaj-kompozíciók**: Több zajforrás keveréke realisztikus helyzetekhez
- **Időbeli változatosság**: Statikus és dinamikusan változó zajok (pl. elhaladó jármű)
- **Frekvenciatartomány-lefedettség**: Alacsony, közepes és magas frekvenciájú zajok egyenletes reprezentációja

### 1.6 Adatbázis-integrációs folyamat

1. **Előkészítő feldolgozás**:
   - Normalizálás: Minden minta azonos hangerőszintre igazítása
   - Mintavételezési frekvencia egységesítése: 16 kHz standardizálás minden hangfájlon
   - Szegmentálás: Egységes 1-2 másodperces minták

2. **Adatkeverés és augmentálás**:
   - Szintetikus és természetes felvételek arányának beállítása
   - A meglévő mikrofononos felvételek integrálása referenciapontként
   - Háttérzajok hozzáadása a tiszta mintákhoz különböző SNR értékekkel

3. **Validációs teszthalmazok létrehozása**:
   - Tiszta tesztminták elkülönítése
   - Valós környezetből származó tesztminták
   - Szélsőséges esetek gyűjteménye (nagyon zajos, szokatlan akcentus)

4. **Edge Impulse specifikus formázás**:
   - MFCC vagy spektrális jellemzők kivonása
   - Adatcímkézési struktúra optimalizálása
   - Adatszettek kiegyensúlyozása a négy kategória között

## 2. Adatbázis létrehozás professzionálisabb megközelítése

### 2.1 Adatgenerálási keretrendszer kialakítása

- **Konfiguráción alapuló generálás**: YAML vagy JSON konfigurációs fájlok a különböző generálási paraméterek tárolására (akcentusok, beszélők, háttérzajok, SNR értékek)
- **Verziókövetés**: Az egyes adatkészlet-generálások paramétereit és eredményeit verziókövetés alatt tároljuk

### 2.2 Eleven Labs API integráció továbbfejlesztése

- **Batch-feldolgozás**: Párhuzamos API-hívások optimalizálása több szál vagy aszinkron kérések használatával
- **Hibakezelés és újrapróbálkozás**: Automatikus újrapróbálkozás API-hibák esetén
- **Voice cloning**: A saját felvételeid alapján egyedi hangok klónozása autentikusabb eredményekért
- **Stability-Clarity paraméterek szisztematikus variálása**: Különböző értékpárok használata a természetes variabilitás érdekében

### 2.3 Háttérzaj kezelés professzionális megközelítése

- **Zajkönyvtár kialakítása**: Kategorizált és annotált zajkönyvtár létrehozása (környezet típusa, hangosság, spektrális jellemzők)
- **Konvolúciós keverés**: Room impulse response (RIR) profilok használata a valósághű akusztikus környezet szimuláláshoz
- **Dinamikus SNR kontroll**: A jel-zaj arány precíz szabályozása az RMS értékek alapján, nem csak egyszerű keverés
- **Környezeti akusztika szimulálása**: Reverb és tér-szimulációk alkalmazása a különböző környezetekhez

### 2.4 Augmentációs pipeline

Az egyszerű összefűzésen túl:

- **Spektrális augmentáció**: Time masking, frequency masking 
- **Időbeli augmentáció**: Időnyújtás, tömörítés, pitch shifting kontrollált módon
- **Környezeti transzformáció**: Mikrofon-karakterisztikák szimulálása (bandpass szűrés)
- **Kompressziós augmentáció**: Különböző MP3/OGG tömörítési szintek szimulálása

### 2.5 Minőségellenőrzési mechanizmus

- **Automatizált minőségellenőrzés**: SNR kalkuláció, spektrális elemzés a generált minták validálására
- **Felhasználói validációs interfész**: Gyors emberi ellenőrzéshez webes felület 
- **Statisztikai ellenőrzések**: Osztályegyensúly, spektrális lefedettség, akcentus-diverzitás folyamatos monitorozása

### 2.6 Adatpipeline implementáció

Az adatgenerálási folyamat fő lépései:

1. Adatgenerálási terv → Konfigurációs fájl generálása
2. Párhuzamos beszédgenerálás Eleven Labs API-val
3. Zajkönyvtárból intelligens zajkiválasztás és -keverés 
4. Augmentációs pipeline futtatása
5. Minőségellenőrzés és validáció
6. Metaadatok generálása Edge Impulse kompatibilis formátumban
7. Adatkészlet verziókövetése és archiválása

### 2.7 Eszközspecifikus adaptáció

- **Célhardver mikrofon-karakterisztikák szimulálása**: A végső eszköz mikrofonjellemzőinek szimulálása
- **Közelítő és távoli beszéd**: Mikrofontól való távolság szimulálása a hangerőn és frekvencia-karakterisztikákon keresztül
- **On-device validáció**: Validációs protokoll az eszközön való teszteléshez

### 2.8 Automatizált pipeline futtatási környezet

- **Docker konténerek**: Az egész generálási környezet konténerizálása a reprodukálhatóság érdekében
- **CI/CD integráció**: Automatikus adatkészlet-frissítés a forrásfájlok változása esetén
- **Monitoring és jelentéskészítés**: Az adatkészlet statisztikáinak automatikus követése és riportolása

## 3. Kezdeti implementációs lépések

1. Meglévő Python kód átalakítása moduláris szerkezetű projekt struktúrává
2. Konfigurációs rendszer implementálása YAML vagy JSON formátumban
3. Eleven Labs API wrapper továbbfejlesztése batch feldolgozással
4. Strukturált zajkönyvtár kialakítása kategóriákkal és metaadatokkal
5. Fejlett augmentációs technikák implementálása (spektrális, időbeli)
6. Minőségellenőrzési modul létrehozása alapvető audiometrikai mérésekkel
7. Kísérleti adatkészlet generálása és validálása Edge Impulse-ban

## 4. Kategóriák definíciója a szintetikus adatbázisban

### 4.1 "Cheers" kulcsszó kategória
- A fő kulcsszó "cheers" különböző akcentusokkal, kiejtési variációkkal, háttérzajokkal
- Minden mintának tartalmaznia kell a "cheers" szót tisztán felismerhetően
- SNR értékek: 20dB-től 0dB-ig változó értékekkel

### 4.2 Neutrális (Noise) kategória
- Tiszta háttérzajok, emberi beszéd nélkül
- Különböző környezetek: iroda, bár, utca, otthon, stb.
- Statikus és dinamikus zajok egyaránt
- Spektrális lefedettség biztosítása a modell általánosítóképességéhez

### 4.3 Ismeretlen (Unknown) kategória
- Fonetikailag hasonló szavak a "cheers"-hez
- Általános angol nyelvű beszéd részletek, amelyek nem tartalmazzák a kulcsszót
- Számok, parancsszavak és egyéb gyakori kifejezések
- Különböző akcentusokkal és háttérzajokkal, a kulcsszóhoz hasonló körülmények között

### 4.4 Természetes felvételek integrálása
- A mikrofononnal rögzített felvételek integrálása az adatkészletbe
- Ezek referenciakét szolgálnak és segítik a modell valós környezetekben való teljesítményét
- A természetes felvételekhez hasonló augmentációk alkalmazása a szintetikus adatokon
# Red Crewmate — viimeistelty Unity-malli

Referenssikuvan pohjalta tehty punainen avaruushahmo: pyöreä kupolipää, yhtenäinen vartalo ja jalat, sininen kupera visiiri, musta kumireunus ja selkäreppu. Korkeus noin 2 metriä. Unityssä etusuunta +Z, ylöspäin +Y.

## Mukana

- `Assets/RedCrewmate/RedCrewmate.fbx`: neljä ihotettua mesh-osaa, 25 438 kolmiota, UV-kartat, neljän luun Generic-rig.
- `Assets/RedCrewmate/Suit_BaseColor.png`: 1024 × 1024 kangaspinnan väritekstuuri.
- Idle (2 sekuntia) ja Walk (0,8 sekuntia), 30 fps, paikallaan toistuvat animaatiot.
- Unity-editoritoiminto materiaaleille, CapsuleColliderille, Animator Controllerille ja prefabille.
- `Sources/RedCrewmate.blend`: muokattava lähdetiedosto, sisältää myös proseduraalisen kangaspinnan bump-efektin. Unity-versiossa käytetään väritekstuuria.
- `Preview.png` ja `Preview_Back.png`: etu- ja takaviiston renderöinnit.

## Unity-käyttö

1. Kopioi `Assets/RedCrewmate` projektisi `Assets`-kansioon.
2. Odota tuonnin ja skriptien käännön valmistumista.
3. Valitse **Tools > Red Crewmate > Create Prefab**.
4. Vedä `RedCrewmate.prefab` sceneen.
5. Ohjaa kävelyä Animatorin `Walking`-bool-parametrilla: `animator.SetBool("Walking", true);`.

Editoritoiminto asettaa FBX:n Generic-rigin, silmukoi klipit ja luo materiaalit URP-, HDRP- tai Built-in-putkelle. Hahmo aloittaa idle-tilassa. Liikuta hahmoa omalla ohjausskriptillä: kävely on paikallaan, root motion on pois käytöstä. Rigidbodyä ei lisätä. Mallissa ei ole käsivarsia eikä se käytä Humanoid-rigiä.

Jos aiempi versio on jo projektissasi, korvaa paketin tiedostot, poista aiemmin generoidut `RedCrewmate.prefab`, `RedCrewmate.controller` ja kolme `.mat`-tiedostoa (vain jos et ole muokannut niitä itse), ja suorita valikkotoiminto uudelleen. Uudelleensuoritus säilyttää olemassa olevat materiaalit ja controllerin tarkoituksella.

## Muokkaus ja tarkistus

Blender 4.3: `blender -b -t 6 --python tools/create_character.py` generoi mallin, tekstuurin, animaatiot ja renderöinnit uudelleen.

`blender -b -t 2 --python tools/validate_character.py` tuo FBX:n takaisin ja tarkistaa neljä mesh-osaa, UV:t, neljä luuta, normalisoidut painot, molemmat animaatiot sekä kävelyn oikeasti muuttaman geometrian. Tarkistus on ajettu onnistuneesti. Unity-editoria ei ole tässä ympäristössä, joten Unityn tuonti ja editoritoiminto vaativat vielä tarkistuksen omassa projektissasi.

# Writeup: MIA

**CTF:** Spooky CTF  
**Challenge:** MIA  
**Category:** OSINT / Geolocation  
**Points:** 672  
**Author:** LoadInConfusion  
**File:** `Unknown_Photo.png`  
**Flag Format:** `spooky{Site_Name_Here}`  
**Primary Flag:** `spooky{Große_Harzburg}` (or variants: `spooky{Harzburg}`, `spooky{Burg_Harzburg}`, `spooky{Burgberg_Plateau}`)

---

## 1. Challenge Overview

> *"We lost direct contact with an informant days ago after someone caught onto their trail. Most recently, we intercepted some digital traffic, a photo, that may help us determine where the informant went. We are aware that the informant did want to visit a historical site for a drop-off; the individual likely brought them somewhere nearby to hide.*  
> *Flag format: spooky{Site_Name_Here}"*

We are provided with a single image: `Unknown_Photo.png`.

---

## 2. Visual & Artifact Analysis

Examining `Unknown_Photo.png` reveals several distinct forensic artifacts:

```
+-----------------------------------------------------------+
|                                                           |
|    [Grabpflege Sign]                                      |
|    (Cemetery / grave care stake)                          |
|                                                           |
|  [Rock / Stone Slab]               [Freshly Dug Trench]   |
|   - Trail Map Pamphlet                                    |
|   - HarzCard Tourist Pass                                 |
|                                                           |
|                                                           |
|                                                           |
|  [Shovel: "RAZOR-BACK"]                                   |
+-----------------------------------------------------------+
```

### Artifact 1: The Trail Map on the Stone
Cropping and enhancing the paper sign resting on the rock slab:
- **Map Header:** `Burgberg-Plateau`
- **Location Name:** `BAD HARZBURG`
- **Official Organization & URL:**
  - `Förderverein DIE HARZBURG`
  - `www.die-harzburg.de`
- **Trail Destinations & Distances Listed:**
  - `Aussichtsreich 0.1 km` (Plumbohms Aussichtsreich on the Burgberg plateau)
  - `Historischer Rundweg 0.1 km`
  - `Besinnungsweg 0.5 km`
  - `Baumwipfelpfad 0.8 km`
  - `Kreuz des Dt. Ostens 2.5 km`
  - `Rabenklippen / Luchsgehege 4.0 km`
  - `Kaiserweg 17 km`

### Artifact 2: The Tourist Card
Directly below the trail map lies a regional discount tourist pass:
- Card brand: **HarzCard** (`HarzCard ... Harzburg ... Harz`).
- Features the distinctive silhouette of regional Harz castles and monuments.

### Artifact 3: The Cemetery Sign (`Grabpflege`)
At the top left of the trench, a black stake in the soil reads:
- **`Grabpflege`** (German for *"grave maintenance / grave care"*), accompanied by a floral emblem.
- Indicates the photo was taken at an active cemetery where grave sites are maintained.

### Artifact 4: The Shovel
At the bottom of the trench lies a heavy-duty commercial spade:
- Stamped brand: **RAZOR-BACK**.

---

## 3. Geolocation & Historical Context

1. **Town:** **Bad Harzburg** (a historic spa town in Lower Saxony, Germany, located on the northern edge of the Harz mountain range).
2. **The Historical Site:**
   - On the summit of the **Großer Burgberg** (483m above sea level) lies the **Große Harzburg** (commonly known as **Harzburg** or **Burg Harzburg**).
   - Built between 1065 and 1068 by King/Emperor **Henry IV** of the Salian dynasty as a massive imperial castle (*Reichsburg*), it was the site of the famous 1073 Saxon siege and Henry IV's nighttime escape.
   - Today, the plateau features the ruins of the castle, the *Canossasäule* (Canossa column), and an archaeological heritage trail managed by the *Förderverein Historischer Burgberg Bad Harzburg e.V.* (`www.die-harzburg.de`).
3. **The Nearby Hiding Spot:**
   - At the base of the Burgberg, directly connected by footpaths to the plateau, lies the **Alter Friedhof am Burgberg** (Historic Cemetery at the Burgberg), explaining the fresh grave and `Grabpflege` stake.

---

## 4. Flag Formulation

The prompt asks for the name of the **historical site** the informant intended to visit for the drop-off:

- **Primary Historical Site Name:** `Große_Harzburg` (German canonical name) / `Harzburg` / `Burg_Harzburg`
- **Plateau / Location Name:** `Burgberg_Plateau` / `Burgberg`

```text
spooky{Große_Harzburg}
```

*(Note: Depending on CTF normalization, standard alternates include `spooky{Grosse_Harzburg}`, `spooky{Harzburg}`, `spooky{Burg_Harzburg}`, or `spooky{Harzburg_Castle}`).*

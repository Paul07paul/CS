---
workflow: general-video
flow: automation
storyboard: no
message: "Donner envie de réserver quelques jours au Chalet Le Sabot de Vénus à Courchevel Moriond."
destination: reels-tiktok
aspect: 1080x1920
language: fr
audience: "voyageurs (Airbnb / réseaux sociaux)"
length: 47.5s
angle: cinematic-property-tour
---

## Intent

Vidéo Airbnb premium du Chalet Le Sabot de Vénus (Courchevel Moriond 1650) construite
uniquement à partir des 28 photos fournies : mouvements de caméra lents (Ken Burns, sans
déformation), fondus élégants, textes courts. Structure en 10 plans du brief utilisateur,
signature Paul Digital à la fin.

## Assets

- source-photos/photo_01..28.png — photos réelles du chalet (seule référence visuelle).
- assets/logo/* — logo Paul Digital (signature finale).

## Notes

- Aucune photo de terrasse fournie : le plan « vue » utilise la pièce de vie aux baies vitrées (photo 28).
- Photos 720×480 pour la plupart : présentées dans un bandeau cinéma 6:5 sur fond flou de la même photo pour rester nettes en 9:16.
- Carte de réservation générique (pas de marque Airbnb). Neige légère ajoutée uniquement sur les plans extérieurs.
- Musique et sons générés par `audio/make_music.py` et `audio/make_sfx.py` (libres de droits).

## Revision v2 (dynamique) + v2.1

- v2 : version rapide (38 s) avec chiffres animés, typographie cinétique, cartes de services, musique 120 BPM (`audio/make_music_v2.py`, `audio/make_sfx_v2.py`).
- v2.1 : photo de la terrasse fournie (`source-photos/photo_29_terrasse.webp`) utilisée pour la vue panoramique et dans le montage (« comme été ») ; fin « Réservez sur Airbnb » avec le logo Airbnb et un bouton « Réserver » qui passe à « Réservé ✓ » (demande explicite de l'utilisateur).

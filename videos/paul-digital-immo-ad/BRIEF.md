---
workflow: general-video
flow: automation
storyboard: yes
message: "Vous nous envoyez votre annonce, nous nous occupons du reste."
destination: reels-tiktok
aspect: 1080x1920
language: fr
audience: "agences immobilières et professionnels de l'immobilier"
length: 30s
angle: before-after
---

## Intent

Publicité motion design pour **Paul Digital**, service qui transforme les annonces
immobilières classiques (photos + texte) en vidéos modernes, dynamiques et professionnelles.
Style 3D isométrique premium, moderne, professionnel : effets de caméra, zooms, transitions
fluides, textes en 3D, statistiques animées, cartes/localisation. Doit ressembler à une pub
d'une entreprise de marketing immobilier, pas à une démo technique. Usage : Instagram, TikTok,
Facebook, prospection d'agences, portfolio.

Arc voulu : annonce classique → transformation en vidéo premium → bien 3D isométrique dont la
caméra révèle les atouts (extérieur, salon, cuisine, chambres, terrasse, piscine, vue,
emplacement) → « rien à gérer » → bénéfices → CTA.

## Customizations

- Bénéfices à montrer : annonces plus attractives · meilleure mise en valeur des biens ·
  contenu adapté aux réseaux sociaux · plus d'impact auprès des acheteurs et locataires ·
  image plus professionnelle et moderne.
- CTA final : « Donnez une nouvelle dimension à vos annonces immobilières. » puis
  « Envoyez-nous votre annonce. Nous nous occupons du reste. »
- Marque : Paul Digital (pas de logo fourni ; wordmark typographique).

## Notes

- Audio : aucune préférence → vidéo muette, musique ajoutée par l'utilisateur sur la plateforme.
- Aucun asset fourni : tout est dessiné (3D isométrique en CSS/SVG/Three.js), pas de photos réelles.
- Aucun contact (téléphone/site) fourni : ne pas en inventer.

## Revision 2 (user feedback)

- Sons « moins forts et secs, plus doux » + « musique dynamique derrière » → effets adoucis (réverbe, passe-bas) et musique 120 BPM synthétisée (`audio/make_music.py`), mix ≈ −15 LUFS.
- Logo fourni (`assets/logo/source-logo.webp`) intégré et animé en fin de vidéo, présent en haut à droite ; charte passée aux couleurs du logo (marine #0C1929, bleu #1A69FA, fond clair).
- Nouveau brief : salle de bain ajoutée à la visite, fiche du bien (prix, surface, chambres, localisation), message « Vous nous envoyez vos photos et les informations du bien. Nous créons votre vidéo immobilière prête à être publiée. », vidéo finale montrée en 9:16 / 1:1 / 16:9. Durée 36,5 s.
- Slogan du logo « Création de sites web » remplacé à l'écran par « Vidéos immobilières ».

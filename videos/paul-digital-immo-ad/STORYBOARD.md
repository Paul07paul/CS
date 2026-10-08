---
format: 1080x1920
duration: 32s
message: "Vous nous envoyez votre annonce, nous nous occupons du reste."
arc: Annonce plate → Transformation → Visite 3D du bien → Clé en main → Preuve → Bénéfices → CTA
audience: agences immobilières et professionnels de l'immobilier
mode: autonomous
version: v1
---

# Paul Digital — publicité 9:16 (v1)

## Changes from v1

- Utilisateur : « fait la vidéo » / « vas y » → construction directe sans planche de croquis (mode autonome) ; scène 08 = engagements sans chiffres inventés.

## Build notes

- Construit comme 5 sous-compositions (`s1-annonce` 0–5,5 s · `s2-villa` 5,5–16,5 s · `s3-cle` 16,5–20 s · `s4-preuve` 20–26 s · `s5-final` 26–32 s) + fond et viseur dans `index.html`. Durée finale : 32 s.
- 3D isométrique en CSS 3D orthographique (`assets/iso.js`), caméra pilotée par GSAP (accesseurs), sans WebGL.
- Scène 06 : « Et tout ce qui l'entoure. » ; scènes 04–05 : titres « Chaque détail compte. » / « Pièce par pièce. » ajoutés en tête.
- GSAP et polices servis en local (`assets/vendor`, `assets/fonts`) : le CDN jsdelivr est bloqué dans cet environnement.

## Decisions

- **Message** : « Vous nous envoyez votre annonce, nous nous occupons du reste. »
- **Format** : 1080×1920, ~32 s, sans voix off, sans musique (ajoutée sur la plateforme). Texte dans la zone sûre : 180 px libres en haut, 360 px libres en bas (interface TikTok/Reels).
- **Fil conducteur** : un **cadre-viseur doré** (4 coins + point REC). Il se pose sur l'annonce plate au début : on la « filme ». Il reste ensuite le cadre de toute la vidéo, puis se referme sur le logo à la fin.
- **Objet héros** : la **villa 3D isométrique** (Three.js, caméra orthographique). Elle naît en scène 03, est visitée en 04–06 et revient en petit, en rotation, derrière le CTA de la scène 10.
- **Charte** : fond encre bleu nuit `#0E1624`, texte crème `#F3EDE2`, accent or chaud `#D6A55A`, piscine turquoise doux `#5FB3B3` (seulement dans la 3D). « Avant » = gris plat `#9AA0A6` sur papier `#E9E6E1`.
- **Typo** : titres DM Serif Display (serif élégant, immobilier haut de gamme) · texte et étiquettes Montserrat 600–800.
- **Interdits** : pas de dégradé néon, pas de texte en dégradé, pas d'effet diaporama (chaque scène découle de la précédente par un mouvement de caméra), pas d'écran de fin figé sans mouvement ambiant, pas de faux numéro ni de faux site.
- **Plan tenu** : la scène 10, phrase-titre, reste immobile ~1 s pour que la phrase s'imprime.
- **Sens des transitions** : la caméra avance toujours (zoom avant / plongée) ; pas d'aller-retour latéral.

## Frame 1 — L'annonce classique

- scene: Une annonce plate, grise, scrolle dans un fil d'annonces identiques ; le viseur doré s'y pose.
- duration: 2.5s
- transition_in: cut
- status: animated
- src: compositions/s1-annonce.html
- type: hook
- blueprint: kinetic-type-beats (adapt) + rules: waterfall-entry, motion-blur-streak

Un fil vertical d'annonces grises défile vite (flou de mouvement), puis freine sur une carte :
3 vignettes photo plates, « Maison 5 pièces · 140 m² · 485 000 € », 3 lignes de texte gris.
Titre au-dessus : « Votre annonce » / « ressemble à toutes les autres ? ». À 2.0 s, le viseur
doré se referme sur la carte, avec le point REC qui clignote. Interdit : pas de logo de vrai portail.

## Frame 2 — La transformation

- scene: La carte bascule en 3D, les photos se détachent en calques, l'annonce devient une vidéo verticale premium qui joue.
- duration: 3s
- transition_in: zoom-through
- status: animated
- src: compositions/s1-annonce.html
- type: product_intro
- blueprint: video-text-pivot (adapt) + rules: hacker-flip-3d, 3d-text-depth-layers, depth-scatter-assemble

La carte s'incline (rotateX/Y), ses éléments se séparent en couches de profondeur. Le gris vire
à la couleur, les vignettes s'agrandissent en plein cadre. Une barre de lecture dorée progresse,
avec un sous-titre animé « Villa d'architecte · Vue mer ». Texte : « Paul Digital la transforme en » /
« **vidéo premium.** » (le mot en or). La promesse est posée dès la 2e scène.

## Frame 3 — Le bien apparaît en 3D

- scene: La villa isométrique s'assemble bloc par bloc sur un socle flottant.
- duration: 2.5s
- transition_in: zoom-through
- status: animated
- src: compositions/s2-villa.html
- type: feature_showcase
- blueprint: logo-assemble-lockup (adapt : assemblage d'un objet) + rules: depth-scatter-assemble, spring-pop-entrance, orbit-3d-entry

Socle, dalles, murs, baies vitrées, toit-terrasse, piscine, palmiers : chaque élément tombe et
rebondit à sa place (stagger ≤ 0,5 s par groupe). La caméra tourne lentement (orbite de 25°).
Titre en 3D extrudé : « Chaque bien » / « mérite sa mise en scène. »

## Frame 4 — Extérieur, terrasse, piscine

- scene: La caméra plonge sur la terrasse et la piscine ; des étiquettes se plantent comme des épingles.
- duration: 2.5s
- transition_in: camera-move
- status: animated
- src: compositions/s2-villa.html
- type: feature_showcase
- blueprint: camera-journey (B — vol sans curseur) + rules: 3d-camera-flight, coordinate-target-zoom, spring-pop-entrance

Zoom avant (×2,2) sur l'angle piscine. L'eau ondule (shader simple). Des étiquettes crème à
liseré or surgissent sur ressort : « Piscine 10 × 4 m », « Terrasse 45 m² », « Jardin paysager ».

## Frame 5 — Visite des pièces

- scene: Le toit se soulève, la caméra traverse salon → cuisine → chambre ; chaque pièce s'éclaire à son tour.
- duration: 3.5s
- transition_in: camera-move
- status: animated
- src: compositions/s2-villa.html
- type: feature_showcase
- blueprint: spatial-pan-stations (adapt : les pièces sont les « stations ») + rules: multi-phase-camera, depth-of-field-blur

Le toit monte et s'efface (vue en coupe, façon maison de poupée). Trois arrêts de caméra de ~1 s,
chacun avec un éclairage chaud de la pièce et une étiquette : « Salon lumineux 42 m² » ·
« Cuisine équipée » · « 3 chambres · suite parentale ». Mobilier stylisé en volumes simples.

## Frame 6 — Vue & emplacement

- scene: Dézoom : la villa devient une épingle sur une carte isométrique, avec rayons de trajet et points d'intérêt.
- duration: 2.5s
- transition_in: zoom-out
- status: animated
- src: compositions/s2-villa.html
- type: feature_showcase
- blueprint: zoom-out-workspace-reveal + rules: svg-path-draw, spring-pop-entrance

Recul rapide et décéléré : la villa rapetisse sur une carte en tuiles isométriques (rues, mer,
centre-ville). Une épingle dorée tombe, un cercle de 1 km se dessine, les trajets se tracent :
« Plage · 5 min », « Écoles · 8 min », « Centre-ville · 10 min ». Lieux fictifs, sans nom de ville.

## Frame 7 — Clé en main

- scene: Trois étapes en un geste : l'annonce s'envoie, Paul Digital crée, la vidéo arrive prête à publier.
- duration: 3.5s
- transition_in: whip
- status: animated
- src: compositions/s3-cle.html
- type: benefit_highlight
- blueprint: agent-progress-theater (adapt) + rules: svg-path-draw, press-release-spring, stat-bars-and-fills

Une carte d'annonce miniature s'envole dans une enveloppe : ① « Vous envoyez votre annonce ».
Un anneau doré se remplit (montage, motion design, sous-titres) : ② « Nous créons votre vidéo ».
Un téléphone 9:16 reçoit la vidéo, avec une coche : ③ « Prête à publier ».
Titre : « Vous nous envoyez votre annonce. » / « On s'occupe du reste. »

## Frame 8 — Les chiffres

- scene: Trois engagements qui s'affichent en grand, avec compteurs animés.
- duration: 2.5s
- transition_in: zoom-through
- status: animated
- src: compositions/s4-preuve.html
- type: social_proof
- blueprint: dataviz-countup + rules: counting-dynamic-scale, stat-bars-and-fills

« 0 tournage nécessaire » · « 3 formats réseaux sociaux » · « 100 % clé en main ».
Validé par l'utilisateur (« vas-y ») : engagements vérifiables plutôt que statistiques inventées.

## Frame 9 — Les bénéfices

- scene: Les 5 bénéfices s'empilent avec icônes, à côté d'un téléphone qui fait défiler un Reel immobilier.
- duration: 3.5s
- transition_in: camera-move
- status: animated
- src: compositions/s4-preuve.html
- type: benefit_highlight
- blueprint: grid-card-assemble (liste verticale qui s'accumule) + rules: waterfall-entry, svg-icon-enrichment

Coches dorées qui se dessinent une à une :
« Des annonces plus attractives » · « Vos biens mieux mis en valeur » · « Un contenu taillé
pour les réseaux sociaux » · « Plus d'impact auprès des acheteurs et locataires » ·
« Une image plus pro et moderne ». Pastilles Instagram / TikTok / Facebook sur le téléphone
(formes génériques, pas de vrais logos).

## Frame 10 — Une nouvelle dimension

- scene: La villa revient en petit et tourne ; la phrase-titre se pose en 3D et tient.
- duration: 2.5s
- transition_in: zoom-through
- status: animated
- src: compositions/s5-final.html
- type: cta
- blueprint: titlecard-reveal + rules: 3d-text-depth-layers, ambient-glow-bloom

Rappel de la scène 03 : la villa tourne lentement sous un halo or. Texte extrudé :
« Donnez une **nouvelle dimension** » / « à vos annonces immobilières. » Il reste immobile ~1 s
(plan tenu).

## Frame 11 — Appel à l'action

- scene: Le viseur doré se referme sur le logo Paul Digital ; la phrase finale s'affiche.
- duration: 3s
- transition_in: cut
- status: animated
- src: compositions/s5-final.html
- type: branding
- blueprint: logo-assemble-lockup + rules: kinetic-beat-slam, ambient-glow-bloom

« Envoyez-nous votre annonce. » / « Nous nous occupons du reste. » Puis le logotexte
**PAUL DIGITAL**, avec en dessous « Vidéos immobilières premium ». Les coins du viseur se
referment sur le logo et le point REC s'arrête : la boucle est bouclée. Halo qui respire
jusqu'à la dernière image.

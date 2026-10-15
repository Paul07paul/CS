---
workflow: general-video
flow: automation
storyboard: no
message: "Paul Digital : votre bien mérite mieux qu'une simple annonce."
destination: site-youtube-linkedin
aspect: 1920x1080
language: fr
audience: "agences immobilières, conciergeries, propriétaires vendant ou louant en direct"
length: 60-65s
angle: presentation-du-service
---

## Intent

Vidéo de présentation de **Paul Digital** (vidéos de présentation en motion design + sites
internet dédiés pour biens immobiliers), narrée à la 1re personne par Paul. Texte de
présentation fourni par l'utilisateur, condensé à ~60 s (choix confirmé).

Demande (verbatim) : « je veux une vidéo animé, des transitions propre et créative, dynamique
avec des effets sonores satisfaisants et agréables, de changement de caméra avant, sur le coté,
je veux du wireflame 3d, du glass morphism, je veux une musique dynamique en fond pas trop forte
par rapport à la voix. La voix je la veux plus naturelle, elle fait trop robot. »

## Customizations

- Format 16:9 (confirmé), ≈ 60 s texte condensé (confirmé), voix masculine naturelle (confirmé).
- Voix (v6) : Gemini 3.1 Flash TTS fr-FR, voix « Charon », direction documentaire énergique (accent de France, demandé par l'utilisateur après l'accent canadien d'ElevenLabs). Ancienne voix : ElevenLabs v4 « Charlie » — remplaçait
  Gemini TTS jugé robotique. Alternative générée : « Chris ».
- Musique : ElevenLabs Music (FLORA), 118 BPM, ducking −9 dB + creux médium sous la voix.
- SFX synthétisés localement (`audio/make_audio.py`) : whoosh, pops, clic, scan, ding, impacts.
- Wireframe 3D : moteur canvas maison `assets/wire.js` (chalet, appartement, maison, villa,
  squelette de site), caméra perspective pilotée par GSAP via accesseurs.
- Glassmorphism : cartes, chips, navigateur, lecteur vidéo en verre dépoli.

## References

- Animations de référence (enregistrements d'écran) : textes courbés, cartes UI en verre,
  téléphone 3D, transitions flou/whip, révélation de logo.
- Exemple de bien : vidéo Chalet Moriond 16:9 ; exemple de site : capture « L'Escapade ».

## Notes

- Photos : chalets Moriond et Sabot de Vénus déjà dans le dépôt ; capture du site L'Escapade.
- Aucun chiffre inventé (courbe « attention » sans valeurs). URL de navigateur générique « votre-bien.fr ».

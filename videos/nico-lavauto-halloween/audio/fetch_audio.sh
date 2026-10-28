#!/usr/bin/env bash
# Downloads the FLORA-generated voice, music and SFX (project "Nico Lav'Auto — Halloween reel").
set -euo pipefail
cd "$(dirname "$0")/../assets/audio"
mkdir -p vo sfx
get(){ curl -sSfL -o "$2" "$1"; echo "ok $2"; }
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m17b96k999hmktygb8y5c7qvfn8h4ewy-0.wav vo/l01.wav
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m17c9hvzjt2pe8j6ccwkcabdk58h4hj5-0.wav vo/l02.wav
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m174fb7hbkddcmvpzq0asm86k18h5rkk-0.wav vo/l03.wav
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m1759hwm6avkerz3shbcqw0qx18h4gnq-0.wav vo/l04.wav
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m179tzg97kektj9sca5hc9awt58h58nh-0.wav vo/l05.wav
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m176bkjsxhkj43m34g0nkd98kd8h5p86-0.wav vo/l06.wav
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m174m0xz34bc378jff3p3xdn918h54e1-0.wav vo/l07.wav
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m173y2rk5ng19zywdqgj5rp1mx8h5s6p-0.wav vo/l08.wav
get https://media.flora.ai/node-inputs/2026/10/28/anonymous/040d447d-a0db-49c6-9c2a-337561b7b68f.mp3 music-horror.mp3
get https://media.flora.ai/node-inputs/2026/10/28/anonymous/a4a48ea2-3f57-4d8c-8761-e72e3c89ad99.mp3 music-dyn.mp3
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m17061nayk4t4h7s4k3hm8kk218h4jqt-0.mp3 sfx/door.mp3
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m172wykapf000qxeawv0xxhgsn8h4wat-0.mp3 sfx/whispers.mp3
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m17133bv8kkn09sb89anf82sh18h59ks-0.mp3 sfx/stinger.mp3
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m171v3y4tr4nprdq66n8pv4vwx8h4ss4-0.mp3 sfx/banish.mp3
get https://media.flora.ai/node-inputs/2026/10/28/px75ndmcw1ehfngmx9cb4a66fn8g54d6/gen-m178p64m179kwx4wb9jwcvnvzn8h4qcs-0.mp3 sfx/creak.mp3

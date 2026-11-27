#!/bin/bash
# Versão final com voz. Uso: ./final.sh 1 2 3   (precisa de voz/epXX.m4a)
cd "$(dirname "$0")"
export NODE_PATH=/opt/node-tools/node_modules
for ep in "$@"; do
  tag=$(printf "ep%02d" "$ep")
  python3 segmentar.py "$ep" > "out/$tag-alinhamento.txt" && python3 voz.py "$ep" && node render.mjs "$ep" && python3 trilha.py "$ep" && python3 mixar.py "$ep" && \
  ffmpeg -loglevel error -y -i "out/$tag-sem-audio.mp4" -i "out/$tag-mix.wav" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "out/$tag-final-com-voz.mp4" && echo "pronto $tag"
done

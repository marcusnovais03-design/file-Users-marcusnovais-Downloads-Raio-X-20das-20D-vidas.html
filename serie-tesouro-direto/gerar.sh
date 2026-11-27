#!/bin/bash
# Gera vídeo + trilha de um ou mais episódios. Uso: ./gerar.sh 1 2 3
cd "$(dirname "$0")"
export NODE_PATH=/opt/node-tools/node_modules
for ep in "$@"; do
  tag=$(printf "ep%02d" "$ep")
  node render.mjs "$ep" && python3 trilha.py "$ep" && \
  ffmpeg -loglevel error -y -i "out/$tag-sem-audio.mp4" -i "out/$tag-trilha.wav" -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart "out/$tag-com-trilha.mp4" && echo "pronto $tag"
done

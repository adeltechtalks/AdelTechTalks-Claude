#!/usr/bin/env bash
# Downloads the brand fonts (Google Fonts, OFL) into engine/fonts/
set -e; cd "$(dirname "$0")"; mkdir -p fonts; cd fonts
B=https://raw.githubusercontent.com/google/fonts/main/ofl
curl -sL -o Cairo.ttf "$B/cairo/Cairo%5Bslnt,wght%5D.ttf"
curl -sL -o Montserrat.ttf "$B/montserrat/Montserrat%5Bwght%5D.ttf"
curl -sL -o ReadexPro.ttf "$B/readexpro/ReadexPro%5BHEXP,wght%5D.ttf"
curl -sL -o JetBrainsMono.ttf "$B/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"
echo "fonts ready"

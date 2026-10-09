#!/usr/bin/env bash
# Erzeugt die externen Quell-PDFs in quellen/out/. Danach: uv run build.py
# Voraussetzungen: TeX Live (pdflatex, lualatex, latex, dvips), Ghostscript (ps2pdf),
# Poppler (pdftops), LibreOffice (soffice), Google Chrome oder Chromium.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out build

# --- Formel --------------------------------------------------------------
pdflatex -interaction=nonstopmode -output-directory=build formel.tex >/dev/null
cp build/formel.pdf out/formel-pdflatex.pdf

lualatex -interaction=nonstopmode -output-directory=build formel.tex >/dev/null
cp build/formel.pdf out/formel-lualatex.pdf

# Klassischer Weg über DVI und PostScript, mit Bitmap-Fonts (-Ppk), wie in alten arXiv-PDFs
latex -interaction=nonstopmode -output-directory=build formel.tex >/dev/null
(cd build && dvips -q -Ppk -D 600 -o formel.ps formel.dvi)
ps2pdf -dEPSCrop build/formel.ps out/formel-dvips.pdf

# --- LibreOffice-Export ---------------------------------------------------
# Eigenes Profil, damit lokale LibreOffice-Einstellungen das Ergebnis nicht beeinflussen
soffice --headless -env:UserInstallation=file://$PWD/build/lo-profile \
  --convert-to pdf --outdir build office.fodt >/dev/null 2>&1
cp build/office.pdf out/office-libreoffice.pdf

# --- Browser "Drucken als PDF" ---------------------------------------------
CHROME=$(command -v google-chrome-stable || command -v chromium || command -v chromium-browser || true)
if [[ -n "$CHROME" ]]; then
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$PWD/out/browser-chrome.pdf" "file://$PWD/browser.html" 2>/dev/null
  # "Drucken" über einen PostScript-Druckertreiber simulieren
  pdftops -level3 out/browser-chrome.pdf build/browser.ps
  ps2pdf build/browser.ps out/browser-postscript.pdf
else
  echo "Kein Chrome/Chromium gefunden, browser-chrome.pdf wird übersprungen" >&2
fi

ls -l out

# Glamour post template v2 (Nov 23, 2026)

Clean layout: one compact text block top-left (hook for the first 2s, then the S/M/XL
tracker + a small "AI model" tag). Nothing in the bottom third or on the right rail,
so TikTok/IG buttons and captions never cover it, and nothing crosses the model's face or outfit.

Setup (fresh container):
  mkdir -p fonts && npm i @fontsource/playfair-display @fontsource/montserrat
  convert playfair-display-latin-{400,500,600}-italic.woff -> fonts/PlayfairItalic{w}.ttf
  and montserrat-latin-{500,600,700}-normal.woff -> fonts/Montserrat-{Medium,SemiBold,Bold}.ttf
  (fontTools: TTFont(woff); f.flavor=None; f.save(ttf))

Use:
  python3 overlays_v2.py ov2
  OV=$PWD/ov2 ./assemble_v2.sh n S.mp4 M.mp4 XL.mp4 out.mp4   # n = Nightly, d = Daily

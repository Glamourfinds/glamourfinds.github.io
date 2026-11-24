#!/usr/bin/env bash
# assemble_v2.sh <n|d> <clipS> <clipM> <clipXL> <out.mp4>
# Clean template (Nov 23 2026): S -> M -> XL with quick crossfades; one compact text
# block top-left (hook for the first 2s, size tracker + small AI tag throughout).
# Nothing in the bottom third or on the right rail, so TikTok/IG UI never covers it.
set -euo pipefail
A="$1"; S="$2"; M="$3"; XL="$4"; OUT="$5"
OV=${OV:-/home/claude/glam/ov2}
T0=${T0:-0.15}; LEN=${LEN:-3.8}; XF=${XF:-0.3}
if [ "$A" = "n" ]; then
  GRADE="curves=all='0/0 0.2/0.17 0.5/0.5 0.8/0.82 1/1',eq=contrast=1.03:saturation=1.02"
else
  GRADE="curves=all='0/0.02 0.25/0.25 0.5/0.52 0.8/0.83 1/1',eq=contrast=1.02:saturation=1.0"
fi
PREP="scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,${GRADE},cas=0.3,fps=30,format=yuv420p,setsar=1"
O1=$(python3 -c "print($LEN-$XF)"); O2=$(python3 -c "print(2*($LEN-$XF))")
ffmpeg -v error -y \
  -ss $T0 -t $LEN -i "$S" -ss $T0 -t $LEN -i "$M" -ss $T0 -t $LEN -i "$XL" \
  -loop 1 -i $OV/${A}_track_S.png -loop 1 -i $OV/${A}_track_M.png -loop 1 -i $OV/${A}_track_XL.png \
  -loop 1 -i $OV/${A}_hook.png \
  -filter_complex "
  [0:v]${PREP}[c0];[1:v]${PREP}[c1];[2:v]${PREP}[c2];
  [3:v]format=rgba,trim=duration=$LEN[s0];[4:v]format=rgba,trim=duration=$LEN[s1];[5:v]format=rgba,trim=duration=$LEN[s2];
  [c0][s0]overlay=0:0:shortest=1[v0];[c1][s1]overlay=0:0:shortest=1[v1];[c2][s2]overlay=0:0:shortest=1[v2];
  [v0][v1]xfade=transition=fade:duration=$XF:offset=$O1[x1];
  [x1][v2]xfade=transition=fade:duration=$XF:offset=$O2[x2];
  [6:v]format=rgba,fade=t=out:st=1.8:d=0.3:alpha=1[hook];
  [x2][hook]overlay=0:0:enable='lt(t,2.2)':shortest=1,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -preset veryfast -crf 18 -profile:v high -pix_fmt yuv420p -r 30 -movflags +faststart -an "$OUT"
ffprobe -v error -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 "$OUT"

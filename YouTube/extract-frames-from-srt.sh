#!/bin/bash

VIDEO="GlyphMiner.mkv"
SUBTITLES="GlyphMiner.srt"
OUTDIR="frames"
MAPFILE="frame_map.txt"

mkdir -p "$OUTDIR"
rm -f "$MAPFILE"

INDEX=1

grep --line-buffered -E '^[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}' "$SUBTITLES" | while read -r line
do
    START=$(echo "$line" | cut -d' ' -f1)
    FFMPEG_TIME=${START/,/.}
    PADDED_INDEX=$(printf "%03d" "$INDEX")

    OUTPUT="$OUTDIR/frame${PADDED_INDEX}.png"
    ffmpeg -loglevel error -ss "$FFMPEG_TIME" -i "$VIDEO" -frames:v 1 "$OUTPUT"

    echo "frame${PADDED_INDEX}.png -> Subtitle $INDEX" >> "$MAPFILE"

    INDEX=$((INDEX + 1))
done

echo "✅ Done! Extracted $((INDEX - 1)) frames. Mapping saved to '$MAPFILE'."

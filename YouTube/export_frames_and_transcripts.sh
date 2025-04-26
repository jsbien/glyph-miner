#!/bin/bash

# === Configurable paths ===
VIDEO_DIR="./frames"                      # Folder with all frames
COLLECTION_FILE="selected-frames.gqv"      # Your saved Geeqie collection
FULL_SRT="glyph-miner.srt"                 # The correct transcript: .srt format
FRAME_MAP="frame_map.txt"                  # Map frame -> subtitle

EXPORT_DIR="exported-frames"
TEXT_DIR="frame-texts"
TEX_OUTPUT="frames.tex"

# === Prepare output directories ===
mkdir -p "$EXPORT_DIR"
mkdir -p "$TEXT_DIR"

# === 1. Export selected frames ===
echo "📂 Copying selected frames..."

while read -r filepath; do
    filename=$(basename "$filepath")
    cp "$filepath" "$EXPORT_DIR/$filename"
done < "$COLLECTION_FILE"

# === 2. Create lookup set of selected frames ===
grep -oP 'frame\d+\.png' "$COLLECTION_FILE" > selected-frames.list

# === 3. Rebuild frame -> subtitle mapping ===
declare -A subtitle_to_frame

while read -r line; do
    frame=$(echo "$line" | awk '{print $1}')
    subtitle_num=$(echo "$line" | grep -o '[0-9]\+$')
    subtitle_to_frame[$subtitle_num]=$frame
done < "$FRAME_MAP"

# === 4. Extract transcripts correctly from .srt ===
echo "📝 Extracting transcripts from glyph-miner.srt..."

current_frame=""
subtitle_block=""
subtitle_idx=0

while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^[0-9]+$ ]]; then
        # New subtitle block starting
        subtitle_idx=$line
        subtitle_block=""
    elif [[ "$line" =~ ^[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3} --> ]]; then
        # Timing line, ignore
        continue
    elif [[ -z "$line" ]]; then
        # End of block
        frame=${subtitle_to_frame[$subtitle_idx]}

        if grep -q "$frame" selected-frames.list; then
            # Frame is selected
            current_frame="$frame"
            echo "$subtitle_block" > "$TEXT_DIR/${current_frame%.png}.txt"
        else
            # Frame was deleted; append text to last selected frame
            if [ -n "$current_frame" ]; then
                echo "" >> "$TEXT_DIR/${current_frame%.png}.txt"
                echo "$subtitle_block" >> "$TEXT_DIR/${current_frame%.png}.txt"
            fi
        fi
    else
        # Subtitle text line (can be multiline, join with spaces)
        if [ -z "$subtitle_block" ]; then
            subtitle_block="$line"
        else
            subtitle_block="$subtitle_block $line"
        fi
    fi
done < "$FULL_SRT"

# === 5. Generate LaTeX Beamer slides ===
echo "📄 Creating LaTeX file..."

cat <<EOL > "$TEX_OUTPUT"
\documentclass{beamer}
\usepackage{graphicx}
\usepackage{caption}
\title{Glyph Miner Slides}
\author{}
\date{}
\begin{document}
\frame{\titlepage}
EOL

for frameimg in "$EXPORT_DIR"/*.png; do
    basename=$(basename "$frameimg" .png)
    cat <<EOL >> "$TEX_OUTPUT"

\begin{frame}{$basename}
\includegraphics[width=0.8\textwidth]{$EXPORT_DIR/$basename.png}
\caption*{\input{$TEXT_DIR/$basename.txt}}
\end{frame}

EOL
done

echo '\end{document}' >> "$TEX_OUTPUT"

echo "✅ All done! Generated LaTeX Beamer file: $TEX_OUTPUT"
echo "👉 Compile it with: pdflatex $TEX_OUTPUT"

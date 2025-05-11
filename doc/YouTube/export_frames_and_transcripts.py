#!/usr/bin/env python3

import sys
import os
import shutil
import re

def read_frame_map(frame_map_path):
    frame_to_subtitle = {}
    with open(frame_map_path, 'r') as f:
        for line in f:
            parts = line.strip().split('->')
            if len(parts) == 2:
                frame = parts[0].strip()
                subtitle_number = int(parts[1].strip().replace('Subtitle', '').strip())
                frame_to_subtitle[subtitle_number] = frame
    return frame_to_subtitle

def parse_srt(srt_path):
    subtitles = {}
    with open(srt_path, 'r') as f:
        content = f.read()
    blocks = content.strip().split('\n\n')
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            idx = int(lines[0].strip())
            text = ' '.join(lines[2:]).strip()
            subtitles[idx] = text
    return subtitles

def main():
    if len(sys.argv) != 6:
        print(f"Usage: {sys.argv[0]} frame_map.txt glyph-miner.srt frames/ output/ frames.tex")
        sys.exit(1)

    frame_map_file = sys.argv[1]
    srt_file = sys.argv[2]
    frame_input_dir = sys.argv[3]
    output_dir = sys.argv[4]
    tex_output_file = sys.argv[5]

    exported_frames_dir = os.path.join(output_dir, "exported-frames")
    frame_texts_dir = os.path.join(output_dir, "frame-texts")

    os.makedirs(exported_frames_dir, exist_ok=True)
    os.makedirs(frame_texts_dir, exist_ok=True)

    # List all .png frames
    all_frames = sorted([f for f in os.listdir(frame_input_dir) if f.endswith('.png')])

    frame_to_subtitle = read_frame_map(frame_map_file)
    subtitles = parse_srt(srt_file)

    selected_frame_set = set(all_frames)

    # Build mapping: subtitle -> frame (if any)
    subtitle_idx_list = sorted(subtitles.keys())
    current_frame = None

    frame_contents = {}

    for idx in subtitle_idx_list:
        frame = frame_to_subtitle.get(idx, None)
        if frame in selected_frame_set:
            current_frame = frame
            frame_contents.setdefault(current_frame, []).append(subtitles[idx])
        elif current_frame:
            frame_contents.setdefault(current_frame, []).append(subtitles[idx])

    # Copy frames and save texts
    for frame_name in all_frames:
        source_path = os.path.join(frame_input_dir, frame_name)
        if os.path.exists(source_path):
            shutil.copy2(source_path, os.path.join(exported_frames_dir, frame_name))
        else:
            print(f"⚠️ Warning: Frame not found: {source_path}")

    for frame, texts in frame_contents.items():
        text_path = os.path.join(frame_texts_dir, frame.replace('.png', '.txt'))
        with open(text_path, 'w') as f:
            f.write('\n\n'.join(texts))

    # Write LaTeX file
    with open(tex_output_file, 'w') as tex:
        tex.write(r"""\documentclass{beamer}
\setbeameroption{show notes on second screen}
\usepackage{graphicx}
\title{Glyph Miner Slides}
\author{}
\date{}
\begin{document}
\frame{\titlepage}
""")
        for frame in sorted(frame_contents.keys()):
            frame_base = frame.replace('.png', '')
            tex.write(f"""
\\begin{{frame}}{{{frame_base}}}
\\includegraphics[width=0.8\\textwidth]{{{os.path.join(exported_frames_dir, frame)}}}
\\note{{\\input{{{os.path.join(frame_texts_dir, frame_base + '.txt')}}}}}
\\end{{frame}}
""")
        tex.write(r"""\end{document}
%%% To do: & normal
%%% Local Variables:
%%% mode: latex
%%% ispell-local-dictionary: "english"
%%% TeX-master: t
%%% coding: utf-8-unix
%%% TeX-PDF-mode: t
%%% TeX-engine: luatex
%%% End:
""")

    print(f"✅ Done! LaTeX file written to {tex_output_file}")

if __name__ == "__main__":
    main()

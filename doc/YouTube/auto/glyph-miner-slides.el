;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "glyph-miner-slides"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("beamer" "")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("graphicx" "") ("caption" "") ("appendixnumberbeamer" "")))
   (TeX-run-style-hooks
    "latex2e"
    "beamer"
    "beamer10"
    "graphicx"
    "caption"
    "appendixnumberbeamer"))
 :latex)


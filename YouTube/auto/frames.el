;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "frames"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("beamer" "")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("graphicx" "")))
   (add-to-list 'LaTeX-verbatim-environments-local "semiverbatim")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "href")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperimage")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperbaseurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "nolinkurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (TeX-run-style-hooks
    "latex2e"
    "output/frame-texts/frame001"
    "output/frame-texts/frame002"
    "output/frame-texts/frame003"
    "output/frame-texts/frame005"
    "output/frame-texts/frame006"
    "output/frame-texts/frame007"
    "output/frame-texts/frame008"
    "output/frame-texts/frame009"
    "output/frame-texts/frame010"
    "output/frame-texts/frame011"
    "output/frame-texts/frame012"
    "output/frame-texts/frame013"
    "output/frame-texts/frame014"
    "output/frame-texts/frame015"
    "output/frame-texts/frame016"
    "output/frame-texts/frame017"
    "output/frame-texts/frame018"
    "output/frame-texts/frame020"
    "output/frame-texts/frame021"
    "output/frame-texts/frame022"
    "output/frame-texts/frame023"
    "output/frame-texts/frame024"
    "output/frame-texts/frame025"
    "output/frame-texts/frame026"
    "output/frame-texts/frame028"
    "output/frame-texts/frame029"
    "output/frame-texts/frame031"
    "output/frame-texts/frame032"
    "output/frame-texts/frame033"
    "output/frame-texts/frame034"
    "output/frame-texts/frame035"
    "output/frame-texts/frame036"
    "output/frame-texts/frame037"
    "output/frame-texts/frame038"
    "output/frame-texts/frame039"
    "output/frame-texts/frame040"
    "output/frame-texts/frame041"
    "output/frame-texts/frame043"
    "output/frame-texts/frame044"
    "output/frame-texts/frame046"
    "output/frame-texts/frame047"
    "output/frame-texts/frame049"
    "output/frame-texts/frame051"
    "output/frame-texts/frame053"
    "output/frame-texts/frame054"
    "output/frame-texts/frame055"
    "output/frame-texts/frame057"
    "output/frame-texts/frame058"
    "output/frame-texts/frame060"
    "output/frame-texts/frame061"
    "beamer"
    "beamer10"
    "graphicx"))
 :latex)


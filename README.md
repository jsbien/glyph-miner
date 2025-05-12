In preparation



# The Glyph Miner version 0.2-alpha software package

![Web Interface](https://img.shields.io/badge/interface-web--based-brightgreen)
![Fork](https://img.shields.io/badge/fork-Python3%20port-blue)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

Glyph Miner is a software for rapidly extracting glyph occurrences from early
typeset prints. 

This is the port of the original Glyph Miner to Python 3 [not yet
working] made by [AsktheCode](https://docs.askthecode.ai/) under the
supervision of [Janusz S. Bień](https://orcid.org/0000-0001-5006-8183)
(or vice versa ☺)).  The port with some minor improvements is
available in the present repository
(https://github.com/jsbien/glyph-miner) and as a Docker image [not yet
ready].



The original Python2 version 0.1-alpha is available in the repository
https://github.com/benedikt-budig/glyph-miner and as a Docker image
(https://hub.docker.com/r/glyphminer/glyphminer).
The original README is available also [*here*](original_README.md).

The original documentation is rudimentary:

* the presentation at 2016 IEEE/ACM Joint
Conference on Digital Libraries (JCDL)
  * The paper available in particular at https://www1.pub.informatik.uni-wuerzburg.de/pub/budig/papers/JCDL-2016_Budig_vanDijk_Kirchner.pdf
  * The slides from the conference available at https://www.informatik.uni-wuerzburg.de/fileadmin/10030100/Presentation-JCDL2016.pdf

* The Youtube video at https://youtu.be/T-p_kIdsn6k The video has been
transcribed with `whisper` and converted into slides, which are available in
this repository.

The current installation instruction is available [*here*](INSTALL.md).

Some debugging tools are available [*here*](local/).

Some preliminary user documentation is available [*here*](doc/).

Some user utilities  are available [*here*](utils/).

## License
Copyright (C) 2016 Benedikt Budig

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

The LodePNG library used in this software is Copyright (C) 2005-2014 Lode
Vandevenne.


## Acknowledgements by  Benedikt Budig
Special thanks go to [Dr. Thomas van Dijk](http://www1.informatik.uni-wuerzburg.de/en/staff/dijk_thomas_van/)
for contributing his fast implementation for the template matching. In addition,
I want to thank to Dr. Hans-Günter Schmidt and his team of the
[Würzburg University Library](http://www.bibliothek.uni-wuerzburg.de/en/ub_infos/contact/departments/digitization_centre/)
 for their generous support.

## License
Copyright (C) 2016 Benedikt Budig

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

The LodePNG library used in this software is Copyright (C) 2005-2014 Lode
Vandevenne.

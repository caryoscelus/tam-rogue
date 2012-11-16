tam-rogue
=========

rogue-like engine and game development

LAUNCHING
---------
Simply change directory to test/ and launch ./start.sh; this will start both
"graphical" client and client/server (which is combined now).
Alternativly, you could launch them by yourself: src/main/test/testclient.py
and src/gfxclient/curses/main.py; they could not work if not launched from
thier directory.

PLAYING
-------
Currenly supported actions:

    KEY             ACTION
    hjklyubn        moving
    F               "fight" (actually just decrease hp for now)
    X               commit suicide
    
    i               show inventory (doesn't work much currently)
    !               show game log

LICENSE
-------
(see full text in file GPL3)

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

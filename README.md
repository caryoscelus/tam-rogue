tam-rogue
=========

rogue-like engine and game development

INTRO
-----
If you came here because you thought that you could play game, you are here
by mistake. This project is started quite recently and it is not playable.
And i think that when real game would appear, it will be in separate
repository, current will contain only engine.

So, if you're not interested in development , you can just add this repo to
bookmarks and return to see what happened to it later.

If you are interested in modding or creating your game on top of this engine,
you are too early too: engine core is not done and API could not be
considered stable.

And in case you want to take part in engine development, it's better to just
contact me.

GOALS
-----
* general-purpose engine with modpacks for actual game experience
* server-client architecture and thus theorethical support of multiplayer
* also, previous point makes it possible to easily replace rendering engine
from ncurses one to opengl
* just create certain game(s) which i have in mind

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
    <direction>     moving
    F <direction>   fight
    X               commit suicide
    e               eat something from floor
    >               climb down the stairs
    <               climb up the stairs
    
    i               toggle displaying inventory (doesn't work much currently)
    !               toggle displaying game log

    <direction> is one of standard hjklyubn keys

Game logs are now working and enabled by default, but if you want to get more
logs, you can use src/main/test/testclient.log for more information (this
includes some debug info as well now).

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

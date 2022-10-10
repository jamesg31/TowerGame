# Copyright (c) 2021 James Gardner.
# This file is part of TowerATC (https://github.com/jamesg31/TowerATC).
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <https://www.gnu.org/licenses/>.

from pydoc import visiblename
import pygame
import pygame_gui

class Gui:
    def __init__(self, screen_height, screen_width, altitude, vpath, manager):
        self.manager = manager
        self.container_rect = pygame.Rect((30, screen_height - 200), (205, 170))
        self.container = pygame_gui.core.UIContainer(
            relative_rect=self.container_rect,
            manager=manager,
            visible=False
        )

        self.altitude = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect((0, 120), (100, 50)),
            container=self.container,
            starting_option=str(altitude),
            options_list=[
                "1000",
                "2000",
                "3000",
                "4000",
                "5000",
                "6000",
                "7000",
                "8000",
            ],
            manager=manager,
            visible=True,
        )

        self.vpath = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((105, 120), (50, 50)),
            text="VP",
            manager=manager,
            container=self.container,
            visible=True
        )

        if vpath != None:
            self.vpath.select()
            self.altitude.disable()

        self.elements = [self.altitude, self.vpath]

    def show(self, vpath, leg_destination):
        self.container.show()
        if vpath != None:
            self.vpath.select()
            self.altitude.disable()
        
        if leg_destination != None:
            self.vpath.enable()
        else:
            self.vpath.disable()

    def hide(self):
        self.container.hide()

    def resize(self, screen_height, screen_width):
        self.container.set_position((30, screen_height - 80))
        self.container.update_containing_rect_position()

    def rebuild(self, altitude, vpath):
        self.elements.remove(self.altitude)
        self.altitude.kill()

        self.altitude = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect((0, 120), (100, 50)),
            container=self.container,
            starting_option=str(altitude),
            options_list=[
                "1000",
                "2000",
                "3000",
                "4000",
                "5000",
                "6000",
                "7000",
                "8000",
            ],
            manager=self.manager,
            visible=True,
        )

        self.elements.append(self.altitude)

        if vpath != None:
            self.vpath.select()
            self.altitude.disable()

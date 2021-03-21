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

import pygame
import pygame_gui

class Gui:
    def __init__(self, screen_height, screen_width, cur_alt, manager):
        self.altitude = pygame_gui.elements.ui_drop_down_menu.UIDropDownMenu(
            relative_rect=pygame.Rect((30, screen_height - 80), (100, 50)),
            starting_option=str(cur_alt),
            options_list=['1000', '2000', '3000', '4000', '5000', '6000', '7000', '8000'],
            manager=manager,
            visible=False)

        self.elements = [self.altitude]
    
    def show(self):
        self.altitude.show()

    def hide(self):
        self.altitude.hide()
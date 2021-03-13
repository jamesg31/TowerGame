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

def asdex_pixel(location, data, scale):
    lat, lon = location
    x = (lon - data["asdex_left"]) * scale
    y = (data["asdex_top"] - lat) * scale
    return x, y

class Asdex:
    def __init__(self, data, screen_height, screen_width):
        self.data = data
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.scale = self.screen_height / (self.data["asdex_top"] - self.data["asdex_bottom"])
        self.surface = pygame.Surface((self.screen_width, self.screen_height))
        self.render()

    def render(self):
        self.surface.fill((0,97,122))
        for shape in self.data["shapes"]:
            new_shape = []
            for coord in shape["points"]:
                new_shape.append(asdex_pixel(coord, self.data, self.scale))
            if shape["type"] == "RWAY":
                color = (29, 29, 28)
            elif shape["type"] == "BLDG":
                color = (76, 76, 76)
            else:
                color = (57, 57, 57)
            pygame.draw.polygon(self.surface, color, new_shape)

    def handle_event(self, event):
        pass
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
from . import Scene


class Asdex(Scene):
    def __init__(self, data, screen_height, screen_width):
        super().__init__(
            "asdex",
            data,
            screen_height,
            screen_width,
            {
                "top": data["asdex_top"],
                "bottom": data["asdex_bottom"],
                "left": data["asdex_left"],
                "right": data["asdex_right"],
            },
        )

    def render(self):
        self.surface.fill((0, 97, 122))

        for shape in self.data["shapes"]:
            new_shape = []

            for coord in shape["points"]:
                new_shape.append(self.coord_to_pixel(coord))

            if shape["type"] == "RWAY":
                color = (29, 29, 28)
            elif shape["type"] == "BLDG":
                color = (76, 76, 76)
            else:
                color = (57, 57, 57)

            pygame.draw.polygon(self.surface, color, new_shape)

    def coord_to_pixel(self, location):
        lat, lon = location
        x = (lon - self.data["asdex_left"]) * self.scale
        y = (self.data["asdex_top"] - lat) * self.scale

        return x, y

    def handle_event(self, event):
        pass

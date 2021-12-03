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


class Scene:
    def __init__(self, name, data, screen_height, screen_width, region):
        self.name = name
        self.data = data
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.region = region

        # Scale for the smaller ratio, based on airport data
        self.vert_scale = abs(
            self.screen_height / (self.region["top"] - self.region["bottom"])
        )

        self.hor_scale = abs(
            self.screen_width / (self.region["left"] - self.region["right"])
        )

        self.scale = min(self.vert_scale, self.hor_scale)
        self.surface = pygame.Surface((self.screen_width, self.screen_height))
        self.render()

    def coord_to_pixel(self, location):
        lat, lon = location
        x = (lon - self.region["left"]) * self.scale
        y = (self.region["top"] - lat) * self.scale
        return x, y

    # Must be overridden by subclass
    def render(self):
        raise NotImplementedError()

    def label(self):
        raise NotImplementedError()
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

        self.runway_start = self.coord_to_pixel(
            (self.data["runway"]["start_lat"], self.data["runway"]["start_long"])
        )

        self.runway_end = self.coord_to_pixel(
            (self.data["runway"]["end_lat"], self.data["runway"]["end_long"])
        )

        ydif = (self.runway_start[1] - self.runway_end[1]) / 2
        xdif = (self.runway_start[0] - self.runway_end[0]) / 2

        self.final = (self.runway_start[0] + xdif, self.runway_start[1] + ydif)
        self.upwind = (self.runway_end[0] - xdif, self.runway_end[1] - ydif)

        self.rbase = (self.final[0] + ydif / 1, self.final[1] - xdif / 1)
        self.lbase = (self.final[0] - ydif / 1, self.final[1] + xdif / 1)

        self.rdownwind = (self.upwind[0] + ydif / 1, self.upwind[1] - xdif / 1)
        self.ldownwind = (self.upwind[0] - ydif / 1, self.upwind[1] + xdif / 1)

        self.extended_final = (
            self.runway_start[0] + (xdif * 3),
            self.runway_start[1] + (ydif * 3),
        )

        self.render()

    def coord_to_pixel(self, location):
        lat, lon = location
        x = (lon - self.region["left"]) * self.scale
        y = (self.region["top"] - lat) * self.scale
        return x, y

    def pixel_to_coord(self, location):
        x, y = location
        lon = (x / self.scale) + self.region["left"]
        lat = ((y / self.scale) - self.region["top"]) * -1
        return lat, lon

    # Must be overridden by subclass
    def render(self):
        raise NotImplementedError()

    def label(self):
        raise NotImplementedError()
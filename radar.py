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

class Radar:
    def __init__(self, data, screen_height, screen_width):
        self.name = "radar"
        self.data = data
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.scale = self.screen_height / (self.data["top"] - self.data["bottom"])
        self.surface = pygame.Surface((self.screen_width, self.screen_height))
        self.render()

    def render(self):
        self.surface.fill((0, 0, 0))
        self.runway_start = self.cood_to_pixel((self.data["runway"]["start_lat"], self.data["runway"]["start_long"]))
        self.runway_end = self.cood_to_pixel((self.data["runway"]["end_lat"], self.data["runway"]["end_long"]))
        pygame.draw.line(self.surface, (255, 255, 255), self.runway_start, self.runway_end, width=3)
        for line in self.data["lines"]:
            pygame.draw.line(self.surface, (255, 255, 255), self.cood_to_pixel((line["start_lat"], line["start_long"])), self.cood_to_pixel((line["end_lat"], line["end_long"])))
        
    def cood_to_pixel(self, location):
        lat, lon = location
        x = (lon - self.data["left"]) * self.scale
        y = (self.data["top"] - lat) * self.scale
        return x, y

    def handle_event(self, event):
        pass
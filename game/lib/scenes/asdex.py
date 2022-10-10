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

    def label(self, aircraft, selected, label_sweep):
        # Change color if aircraft is selected
        if selected == aircraft:
            aircraft.color = (174, 179, 36)
        else:
            aircraft.color = (86, 176, 91)
        aircraft.textSurf.fill(pygame.Color(0, 0, 0, 0))
        aircraft.textSurf.set_alpha(255)

        # Determine display text and size
        displayText1 = f"{aircraft.name} "
        displayText2 = f"{aircraft.aircraft_type} {aircraft.speed} "
        # Determine the x, y size of displayText according to pygame
        # Then add 5 because it's slightly too small (shrug)
        displaySize = tuple(n + 5 for n in aircraft.font.size(displayText1))

        # Clear and redraw the text surface
        aircraft.textSurf1 = aircraft.font.render(str(displayText1), 1, aircraft.color)
        aircraft.textSurf2 = aircraft.font.render(str(displayText2), 1, aircraft.color)
        aircraft.surf = pygame.Surface(
            (displaySize[0], displaySize[1] * 2), pygame.SRCALPHA
        )
        aircraft.super_surf = pygame.Surface(
            (displaySize[0], displaySize[1] * 2), pygame.SRCALPHA
        )
        pygame.draw.rect(
            aircraft.surf,
            aircraft.color,
            (0, ((displaySize[1] * 2 - 10) / 2) - 2.5, 5, 5),
        )
        aircraft.surf.blit(aircraft.textSurf1, (9, 0))
        aircraft.surf.blit(aircraft.textSurf2, (9, displaySize[1] - 5))

        # Creates offset to move the aircraft up when rendering
        # with size of text so small square is at actual position instead of top left corner
        aircraft.y_offset = (displaySize[1] * 2 - 10) / 2

        aircraft.x_sup_offset = 0
        aircraft.y_sup_offset = 0

        x, y = self.coord_to_pixel((aircraft.y, aircraft.x))
        # Moves the rect to the new location of the text, used for collisions
        aircraft.rect.update(
            (x, y-aircraft.y_offset),
            (displaySize[0], (displaySize[1] - 5) * 2)
        )

        aircraft.super_surf.blit(aircraft.surf, (0, 0))
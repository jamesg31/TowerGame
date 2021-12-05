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
from pygame import draw
from . import Scene
from ..tools import draw_line_dashed


class Radar(Scene):
    def __init__(self, data, screen_height, screen_width):
        super().__init__(
            "radar",
            data,
            screen_height,
            screen_width,
            {
                "top": data["top"],
                "bottom": data["bottom"],
                "left": data["left"],
                "right": data["right"],
            },
        )

    def render(self):
        self.surface.fill((0, 0, 0))

        self.runway_start = self.coord_to_pixel(
            (self.data["runway"]["start_lat"], self.data["runway"]["start_long"])
        )

        self.runway_end = self.coord_to_pixel(
            (self.data["runway"]["end_lat"], self.data["runway"]["end_long"])
        )

        pygame.draw.line(
            self.surface, (255, 255, 255), self.runway_start, self.runway_end, width=3
        )

        ydif = (self.runway_start[1] - self.runway_end[1]) / 2
        xdif = (self.runway_start[0] - self.runway_end[0]) / 2
        ratio = ydif / xdif

        final = (self.runway_start[0] + xdif, self.runway_start[1] + ydif)
        upwind = (self.runway_end[0] - xdif, self.runway_end[1] - ydif)

        rbase = (final[0] + ydif / 1, final[1] - xdif / 1)
        lbase = (final[0] - ydif / 1, final[1] + xdif / 1)

        rdownwind = (upwind[0] + ydif / 1, upwind[1] - xdif / 1)
        ldownwind = (upwind[0] - ydif / 1, upwind[1] + xdif / 1)

        extended_final = (
            self.runway_start[0] + (xdif * 3),
            self.runway_start[1] + (ydif * 3),
        )

        draw_line_dashed(self.surface, (86, 176, 91), self.runway_start, extended_final)
        draw_line_dashed(self.surface, (86, 176, 91), self.runway_end, upwind)
        draw_line_dashed(self.surface, (86, 176, 91), final, rbase)
        draw_line_dashed(self.surface, (86, 176, 91), final, lbase)
        draw_line_dashed(self.surface, (86, 176, 91), upwind, rdownwind)
        draw_line_dashed(self.surface, (86, 176, 91), upwind, ldownwind)
        draw_line_dashed(self.surface, (86, 176, 91), rdownwind, rbase)
        draw_line_dashed(self.surface, (86, 176, 91), ldownwind, lbase)

        for line in self.data["lines"]:
            pygame.draw.line(
                self.surface,
                (255, 255, 255),
                self.coord_to_pixel((line["start_lat"], line["start_long"])),
                self.coord_to_pixel((line["end_lat"], line["end_long"])),
            )

    def label(self, aircraft, selected, label_sweep):
        # Change color if aircraft is selected
        if selected == aircraft:
            aircraft.color = (174, 179, 36)
        else:
            aircraft.color = (86, 176, 91)
        aircraft.textSurf.fill(pygame.Color(0, 0, 0, 0))
        aircraft.textSurf.set_alpha(255)

        # Convert altitudes to three didget standard
        if aircraft.altitude < 1000:
            altitude = "00" + str(aircraft.altitude)[0]
        elif aircraft.altitude >= 1000 and aircraft.altitude < 10000:
            altitude = "0" + str(aircraft.altitude)[0:2]
        else:
            altitude = str(aircraft.altitude)[0:3]

        if aircraft.target_altitude < 1000:
            target_altitude = "00" + str(aircraft.target_altitude)[0]
        elif aircraft.target_altitude >= 1000 and aircraft.altitude < 10000:
            target_altitude = "0" + str(aircraft.target_altitude)[0:2]
        else:
            target_altitude = str(aircraft.target_altitude)[0:3]

        # Determine display text and size
        displayText1 = f"{aircraft.name} "
        displayText2 = f"{altitude} {aircraft.speed}  "
        displayText3 = f"{target_altitude} {aircraft.aircraft_type} "
        # Determine the x, y size of displayText according to pygame
        # Then add 5 because it's slightly too small (shrug)
        displaySize = tuple(n + 5 for n in aircraft.font.size(displayText1))

        # Clear and redraw the text surface
        aircraft.textSurf1 = aircraft.font.render(str(displayText1), 1, aircraft.color)
        if label_sweep:
            aircraft.textSurf2 = aircraft.font.render(
                str(displayText2), 1, aircraft.color
            )
        else:
            aircraft.textSurf2 = aircraft.font.render(
                str(displayText3), 1, aircraft.color
            )
        aircraft.surf = pygame.Surface(
            (displaySize[0], displaySize[1] * 2), pygame.SRCALPHA
        )
        pygame.draw.rect(
            aircraft.surf,
            aircraft.color,
            (0, ((displaySize[1] * 2 - 10) / 2) - 2.5, 5, 5),
        )
        aircraft.surf.blit(aircraft.textSurf1, (9, 0))
        aircraft.surf.blit(aircraft.textSurf2, (9, displaySize[1] - 5))

        # Moves the rect to the new location of the text, used for collisions
        aircraft.rect.update(
            self.coord_to_pixel((aircraft.y, aircraft.x)),
            (displaySize[0], displaySize[1] * 2),
        )

        # Creates offset to move the aircraft up when rendering
        # with size of text so small square is at actual position instead of top left corner
        aircraft.offset = (displaySize[1] * 2 - 10) / 2
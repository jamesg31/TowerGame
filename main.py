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
import hjson
import json
from math import sin, cos, sqrt, atan2, radians
from asdex import Asdex
from radar import Radar

with open('airport.hjson') as f:
  airport_data = hjson.loads(f.read())
  #airport_data = json.load(f)

def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 3444

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (sin(dlat / 2) * sin(dlat / 2) +
         cos(radians(lat1)) * cos(radians(lat2)) *
         sin(dlon / 2) * sin(dlon / 2))
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = radius * c
    return d

screen_width = 1200
screen_height = 600
frame_rate = 30
scene = True
debug = False

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))

class Aircraft(pygame.sprite.Sprite):
    def __init__(self, loc, speed, heading, name, altitude):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.surf = pygame.Surface((750, 15), pygame.SRCALPHA)
        # Draw dot to the left of text
        pygame.draw.rect(self.surf, (86, 176, 91), (0, 7.5, 5, 5))
        self.font = pygame.font.Font("font.ttf", 15)
        self.textSurf = self.font.render(name, 1, (86, 176, 91))
        # self.surf.blit(self.textSurf, (9, 0))
        self.rect=self.surf.get_rect()
        self.y, self.x = loc
        self.heading = heading
        self.speed = speed
        self.altitude = altitude

    def update(self, elapsed, scene):
        # Calculate speed in km / second, then multiply by seconds since last update
        self.h = (self.speed / 3600 * (elapsed / 1000)) * 60
        # Calculate difference to lat and lon using km to cood conversions
        self.y += (cos(radians(self.heading)) * (self.h / 110.574))
        self.x += (sin(radians(self.heading)) * (self.h / (111.320 *cos(self.y))))
        self.label()

    def label(self):
        aircraft.textSurf.fill(pygame.Color(0, 0, 0, 0))
        aircraft.textSurf.set_alpha(255)
        # Determine display text and size
        if debug:
            displayText = f'{self.name} | {self.altitude}     '
        else:
            displayText = f'{self.name}     '
        # Determine the x, y size of displayText according to pygame
        # Then add 5 because it's slightly too small (shrug)
        displaySize = tuple(n + 5 for n in self.font.size(displayText))

        # Clear and redraw the text surface
        self.textSurf = self.font.render(str(displayText), 1, (86, 176, 91))
        self.surf = pygame.Surface(displaySize, pygame.SRCALPHA)
        pygame.draw.rect(self.surf, (86, 176, 91), (0, 7.5, 5, 5))
        self.surf.blit(self.textSurf, (9, 0))

asdex = Asdex(airport_data, screen_height, screen_width)
radar = Radar(airport_data, screen_height, screen_width)
aircrafts = pygame.sprite.Group()
aircrafts.add(Aircraft(
    (32.72426133333333, -117.212722), 250, 45, 'Plane1', 6000))
aircrafts.add(Aircraft(
    (32.73710425, -117.20420971), 18, 180, 'Plane2', 0))
elapsed = 1
sweep = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                scene = not scene
            # F1 to toggle "debug mode"
            if event.key == pygame.K_F1:
                debug = not debug
                for aircraft in aircrafts:
                    aircraft.label()
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if debug:
                if scene:
                    print((x / asdex.scale) + airport_data["asdex_left"])
                    print(((y / asdex.scale) - airport_data["asdex_top"]) * -1)
                else:
                    print((x / radar.scale) + airport_data["left"])
                    print(((y / radar.scale) - airport_data["top"]) * -1)

    if not scene:
        screen.blit(radar.surface, (0, 0))
        for aircraft in aircrafts:
            if sweep % 60 == 0:
                aircraft.update(elapsed, scene)
            screen.blit(aircraft.surf, radar.cood_to_pixel((aircraft.y, aircraft.x)))

    else:
        screen.blit(asdex.surface, (0, 0))
        for aircraft in aircrafts:
            if sweep % 60 == 0:
                aircraft.update(elapsed, scene)
            screen.blit(aircraft.surf, asdex.cood_to_pixel((aircraft.y, aircraft.x)))
    
    sweep += 1
        
    pygame.display.flip()
    elapsed = clock.tick(frame_rate)
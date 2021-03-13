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
px_per_nm = screen_height / distance((airport_data["top"], 0), (airport_data["bottom"], 0))

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))

class Aircraft(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.Surface((75, 15), pygame.SRCALPHA)
        pygame.draw.rect(self.surf, (86, 176, 91), (0, 7.5, 5, 5))
        self.font = pygame.font.Font("font.ttf", 15)
        self.textSurf = self.font.render("UAL121", 1, (86, 176, 91))
        self.surf.blit(self.textSurf, (9, 0))
        self.rect=self.surf.get_rect()
        self.x = 600 / radar.scale
        self.y = 300 / radar.scale
        self.heading = 60
        self.speed = 250
    
    def update(self, elapsed):
        self.h = ((self.speed * px_per_nm) / 3600 * (elapsed / 1000)) * 60
        self.x += (sin(radians(self.heading)) * self.h) / radar.scale
        self.y -= (cos(radians(self.heading)) * self.h) / radar.scale

asdex = Asdex(airport_data, screen_height, screen_width)
radar = Radar(airport_data, screen_height, screen_width)
aircraft = Aircraft()
elapsed = 1
sweep = 0
running = True
scene = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                scene = not scene

    if not scene:
        screen.blit(radar.surface, (0, 0))
        if sweep % 60 == 0:
            aircraft.update(elapsed)
        sweep += 1
        screen.blit(aircraft.surf, (aircraft.x * radar.scale, aircraft.y * radar.scale))
    
    else:
        screen.blit(asdex.surface, (0, 0))
        
    pygame.display.flip()
    elapsed = clock.tick(frame_rate)
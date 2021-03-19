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
debug = False

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height))
manager = pygame_gui.UIManager((screen_width, screen_height), 'theme.json')

altitude_dropdown = pygame_gui.elements.ui_drop_down_menu.UIDropDownMenu(
    relative_rect=pygame.Rect((30, screen_height - 80), (100, 50)),
    starting_option='',
    options_list=['1000', '2000', '3000', '4000', '5000', '6000', '7000', '8000'],
    manager=manager,
    visible=False)

gui_elements = [altitude_dropdown]

class Aircraft(pygame.sprite.Sprite):
    def __init__(self, loc, speed, heading, name, altitude):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.color = (86, 176, 91)
        self.surf = pygame.Surface((750, 15), pygame.SRCALPHA)
        # Draw dot to the left of text
        pygame.draw.rect(self.surf, self.color, (0, 7.5, 5, 5))
        self.font = pygame.font.Font("font.ttf", 15)
        self.textSurf = self.font.render(name, 1, self.color)
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
        # Change color if aircraft is selected
        if selected == self:
            self.color = (174, 179, 36)
        else:
            self.color = (86, 176, 91)
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
        self.textSurf = self.font.render(str(displayText), 1, self.color)
        self.surf = pygame.Surface(displaySize, pygame.SRCALPHA)
        pygame.draw.rect(self.surf, self.color, (0, 7.5, 5, 5))
        self.surf.blit(self.textSurf, (9, 0))

        # Moves the rect to the new location of the text, used for collisions
        self.rect.update(scene.cood_to_pixel((self.y, self.x)), displaySize)

    def change_altitude(self, altitude):
        self.altitude = altitude

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
scene = asdex
selected = None
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if scene.name == "asdex":
                    scene = radar
                else:
                    scene = asdex
            # F1 to toggle "debug mode"
            if event.key == pygame.K_F1:
                debug = not debug
                for aircraft in aircrafts:
                    aircraft.label()
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            collide = False
            # Detect aircraft clicks
            for aircraft in aircrafts:
                if aircraft.rect.collidepoint(x, y):
                    collide = True
                    selected = aircraft
                    # Update all aircraft colors
                    for aircraft in aircrafts:
                        aircraft.label()

                    altitude_dropdown.selected_option = str(selected.altitude)
                    altitude_dropdown.show()
                
            # Check if click is inside a gui element
            for gui_element in gui_elements:
                if gui_element.hover_point(x, y) or gui_element.is_focused:
                    collide = True

            # If no collision, unselect aircraft
            if not collide:
                selected = None
                for aircraft in aircrafts:
                    aircraft.label()
                
                show_gui = False
                altitude_dropdown.hide()
  
            # If in debug mode, print cood of screen click
            if debug:
                if scene.name == "asdex":
                    print((x / asdex.scale) + airport_data["asdex_left"])
                    print(((y / asdex.scale) - airport_data["asdex_top"]) * -1)
                else:
                    print((x / radar.scale) + airport_data["left"])
                    print(((y / radar.scale) - airport_data["top"]) * -1)     

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == altitude_dropdown:
                    selected.change_altitude(int(event.text))

        manager.process_events(event)

    screen.blit(scene.surface, (0, 0))
    for aircraft in aircrafts:
        if sweep % 60 == 0:
            aircraft.update(elapsed, scene)
        screen.blit(aircraft.surf, scene.cood_to_pixel((aircraft.y, aircraft.x)))
    
    sweep += 1
    
    manager.update(elapsed / 1000)
    manager.draw_ui(screen)
    pygame.display.update()
    elapsed = clock.tick(frame_rate)

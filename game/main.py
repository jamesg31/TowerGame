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
import time
from math import sin, cos, atan, radians, degrees, sqrt
import numpy as np
from lib.scenes import Asdex
from lib.scenes import Radar
from lib import Gui

with open("res/airport.hjson") as f:
    airport_data = hjson.loads(f.read())

with open("res/aircraft.hjson") as f:
    aircraft_data = hjson.loads(f.read())

screen_width = 1200
screen_height = 600
frame_rate = 240
debug = False

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
manager = pygame_gui.UIManager((screen_width, screen_height), "res/theme.json")


class Aircraft(pygame.sprite.Sprite):
    def __init__(self, loc, speed, heading, path, altitude, name, aircraft_type):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.color = (86, 176, 91)
        self.surf = pygame.Surface((750, 15), pygame.SRCALPHA)
        self.last_update = time.time()

        # Draw dot to the left of text
        pygame.draw.rect(self.surf, self.color, (0, 7.5, 5, 5))
        self.font = pygame.font.Font("res/font.ttf", 15)
        self.textSurf = self.font.render(name, 1, self.color)

        # self.surf.blit(self.textSurf, (9, 0))
        self.rect = self.surf.get_rect()
        self.y, self.x = loc
        self.heading = heading
        self.speed = speed
        self.altitude = altitude
        self.path = path
        self.stage = 0
        self.target_altitude = altitude
        self.gui = Gui(screen_height, screen_width, self.target_altitude, manager)
        self.aircraft_type = aircraft_type
        self.offset = 0

    def update(self, elapsed, scene):
        # Does aircraft need to climb or descend?
        if self.target_altitude != self.altitude:
            # Calculate rate at which aircraft should climb or descend
            alt_change = (aircraft_data[self.aircraft_type]["vspeed"] / 60) * (
                time.time() - self.last_update
            )

            # Is the aircraft above, below, or close to the target alt
            if self.target_altitude + alt_change <= self.altitude:
                self.altitude -= alt_change
            elif self.target_altitude - alt_change >= self.altitude:
                self.altitude += alt_change
            # Aircraft is within the alt_change of the target altitude
            else:
                self.altitude = self.target_altitude

        # Calculate speed in km / second, then multiply by seconds since last update
        self.h = ((self.speed * 1.852) / 3600) * (time.time() - self.last_update)
        self.last_update = time.time()

        if self.path != None:
            location = radar.coord_to_pixel((self.y, self.x))
            ydif = self.path[self.stage][0] - location[0]
            xdif = self.path[self.stage][1] - location[1]
            if xdif > 0:
                self.heading = 180 - degrees(atan(ydif / xdif))
            elif xdif < 0:
                self.heading = 360 - degrees(atan(ydif / xdif))
            print("heading: " + str(self.heading))
            print("tan: " + str(degrees(atan(ydif / xdif))))
            print("ydif: " + str(ydif))
            print("xdif: " + str(xdif))

        # Calculate difference to lat and lon using km to cood conversions
        self.y += cos(radians(self.heading)) * (self.h / 110.574)
        self.x += sin(radians(self.heading)) * (
            self.h / (111.320 * cos(radians(self.y)))
        )
        self.label()

    def label(self):
        scene.label(self, selected, label_sweep)

    def change_altitude(self, altitude):
        self.target_altitude = altitude


asdex = Asdex(airport_data, screen_height, screen_width)
radar = Radar(airport_data, screen_height, screen_width)
scene = asdex
rpattern = [radar.upwind, radar.rdownwind, radar.rbase, radar.final]
lpattern = [radar.upwind, radar.ldownwind, radar.lbase, radar.final]

aircrafts = pygame.sprite.Group()
aircrafts.add(
    Aircraft((32.72426133333333, -117.212722), 250, 45, None, 6000, "UAL1208", "B738")
)
aircrafts.add(
    Aircraft((32.737167029999995, -117.20439805), 18, 180, None, 0, "N172SP", "C172")
)
aircrafts.add(
    Aircraft(
        (airport_data["runway"]["start_lat"], airport_data["runway"]["start_long"]),
        180,
        None,
        lpattern,
        0,
        "N2203G",
        "C172",
    )
)
elapsed = 1
sweep = 0
label_sweep = True
running = True
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
                    if selected != None:
                        selected.gui.hide()
                    selected = aircraft
                    # Update all aircraft colors
                    for aircraft in aircrafts:
                        aircraft.label()

                    selected.gui.selected_option = str(selected.target_altitude)
                    selected.gui.show()

            # Check if there is a selected aircraft
            if selected != None:
                # Check if click is inside a gui element
                for element in selected.gui.elements:
                    if element.hover_point(x, y) or element.is_focused:
                        collide = True

            # If no collision, unselect aircraft
            if not collide:
                if selected != None:
                    selected.gui.hide()
                    selected = None
                for aircraft in aircrafts:
                    aircraft.label()

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
                if event.ui_element == selected.gui.altitude:
                    selected.change_altitude(int(event.text))
                    for aircraft in aircrafts:
                        aircraft.label()
                    selected.gui.hide()

        manager.process_events(event)

        if event.type == pygame.VIDEORESIZE:
            # Get new size
            w, h = pygame.display.get_surface().get_size()

            # Hide current scene
            scene.surface.fill(pygame.Color(0, 0, 0, 0))
            scene.surface.set_alpha(255)

            # Recreate all scenes with new size
            asdex.__init__(airport_data, h, w)
            radar.__init__(airport_data, h, w)

    screen.blit(scene.surface, (0, 0))

    if sweep == 60:
        label_sweep = not label_sweep
        for aircraft in aircrafts:
            aircraft.update(elapsed, scene)
            if aircraft.path != None:
                x, y = radar.coord_to_pixel((aircraft.y, aircraft.x))
                distance = sqrt(
                    (x - aircraft.path[aircraft.stage][0]) ** 2
                    + (y - aircraft.path[aircraft.stage][1]) ** 2
                )
                if distance < 10:
                    aircraft.stage += 1

        sweep = 0

    sweep += 1

    for aircraft in aircrafts:
        x, y = scene.coord_to_pixel((aircraft.y, aircraft.x))
        screen.blit(aircraft.surf, (x, y - aircraft.offset))

    manager.update(elapsed / 1000)
    manager.draw_ui(screen)
    pygame.display.update()
    elapsed = clock.tick(frame_rate)
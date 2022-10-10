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
from math import sqrt
import numpy as np
from lib.scenes import Asdex, Radar
from lib import Aircraft

with open("res/airport.hjson") as f:
    airport_data = hjson.loads(f.read())

with open("res/aircraft.hjson") as f:
    aircraft_data = hjson.loads(f.read())

screen_width = 1200
screen_height = 600
frame_rate = 30
sweep_sec = 2
debug = False

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
manager = pygame_gui.UIManager((screen_width, screen_height), "res/theme.json")

asdex = Asdex(airport_data, screen_height, screen_width)
radar = Radar(airport_data, screen_height, screen_width)
scene = asdex
rpattern = [radar.upwind, radar.rdownwind, radar.rbase, radar.final]
lpattern = [radar.upwind, radar.ldownwind, radar.lbase, radar.final]

aircrafts = pygame.sprite.Group()
aircrafts.add(
    Aircraft((32.72426133333333, -117.212722), 250, 0, None, None, 6000, "UAL1208", "B738")
)
#aircrafts.add(
#    Aircraft((32.737167029999995, -117.20439805), 18, 180, None, None, 0, "N172SP", "C172")
#)
aircrafts.add(
    Aircraft(
        (airport_data["runway"]["start_lat"], airport_data["runway"]["start_long"]),
        90,
        180,
        lpattern,
        None,
        0,
        "N2203G",
        "C172",
    )
)
aircrafts.add(
    Aircraft(
        None,
        200,
        None,
        None,
        airport_data["arrivals"]["one"],
        None,
        "AAL220",
        "B738"
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
                        selected.hide_route()
                    selected = aircraft
                    # Update all aircraft colors
                    for aircraft in aircrafts:
                        aircraft.label()

                    selected.gui.selected_option = str(selected.target_altitude)
                    selected.gui.show(selected.vpath, selected.leg_destination)
                    selected.show_route()

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
                    selected.hide_route()
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
                    #selected.gui.hide()
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == selected.gui.vpath:
                    if selected.vpath != None:
                        selected.vpath = None
                        selected.gui.rebuild(selected.target_altitude, selected.vpath)
                    else:
                        selected.enable_vpath()

        if event.type == pygame.VIDEORESIZE:
            # Get new size
            w, h = pygame.display.get_surface().get_size()

            # Hide current scene
            scene.surface.fill(pygame.Color(0, 0, 0, 0))
            scene.surface.set_alpha(255)

            # Recreate all scenes with new size
            asdex.__init__(airport_data, h, w)
            radar.__init__(airport_data, h, w)

            # Inform GUIs of new screen size
            manager.set_window_resolution((w, h))
            for aircraft in aircrafts:
                aircraft.gui.resize(h, w)

        manager.process_events(event)

    screen.blit(scene.surface, (0, 0))

    if sweep == sweep_sec * frame_rate:
        label_sweep = not label_sweep
        for aircraft in aircrafts:
            aircraft.update(elapsed, scene, debug)
            if aircraft.pattern != None:
                x, y = radar.coord_to_pixel((aircraft.y, aircraft.x))
                distance = sqrt(
                    (x - aircraft.pattern[aircraft.leg][0]) ** 2
                    + (y - aircraft.pattern[aircraft.leg][1]) ** 2
                )
                if distance < 10:
                    aircraft.leg += 1

        sweep = 0

    sweep += 1

    for aircraft in aircrafts:
        x, y = scene.coord_to_pixel((aircraft.y, aircraft.x))
        screen.blit(aircraft.surf, (x, y - aircraft.offset))

    manager.update(elapsed / 1000)
    manager.draw_ui(screen)
    pygame.display.update()
    elapsed = clock.tick(frame_rate)
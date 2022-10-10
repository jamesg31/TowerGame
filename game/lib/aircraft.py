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
import time
from math import sin, cos, atan, radians, degrees
from .tools import calculate_bearing, calculate_distance
from . import Gui

class Aircraft(pygame.sprite.Sprite):
    def __init__(self, loc, speed, heading, pattern, arrival, altitude, name, aircraft_type):
        from main import screen_height, screen_width, manager
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.color = (86, 176, 91)
        self.surf = pygame.Surface((750, 15), pygame.SRCALPHA)
        self.last_update = time.time()

        # Draw dot to the left of text
        pygame.draw.rect(self.surf, self.color, (0, 7.5, 5, 5))
        self.font = pygame.font.Font("res/font.ttf", 15)
        self.textSurf = self.font.render(name, 1, self.color)

        # Handle arrivals initiation
        self.arrival = arrival
        if self.arrival != None:
            self.altitude = self.arrival[0][1]
            self.y, self.x = self.arrival[0][0]
            self.leg_destination = self.arrival[1][0]
            self.heading = calculate_bearing(self.arrival[0][0], self.leg_destination)
            print(self.heading)
        else:
            self.altitude = altitude
            self.y, self.x = loc
            self.heading=heading
            self.leg_destination = None

        self.rect = self.surf.get_rect()
        self.speed = speed
        self.pattern = pattern
        self.leg = 0
        self.target_altitude = self.altitude
        self.gui = Gui(screen_height, screen_width, self.target_altitude, manager)
        self.aircraft_type = aircraft_type
        self.offset = 0

    def update(self, elapsed, scene, debug):
        from main import radar, airport_data, aircraft_data, sweep_sec      
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

        if self.pattern != None:
            location = radar.coord_to_pixel((self.y, self.x))
            ydif = self.pattern[self.leg][0] - location[0]
            xdif = self.pattern[self.leg][1] - location[1]
            if xdif > 0:
                self.heading = 180 - degrees(atan(ydif / xdif))
            elif xdif < 0:
                self.heading = 360 - degrees(atan(ydif / xdif))
            if debug:
                print("heading: " + str(self.heading))
                print("tan: " + str(degrees(atan(ydif / xdif))))
                print("ydif: " + str(ydif))
                print("xdif: " + str(xdif))
                print ("tl: " + str(self.rect.topleft))
                print ("br: " + str(self.rect.bottomright))

        elif self.arrival != None:
            # check if at the end of the leg
                # if at end, turn, recalculate vs and turn
                # if last leg, turn to runway
                # if runway, land
            # Calculate distance traveled per sweep
            km_per_sweep = ((self.speed * 1.852) / 3600) * sweep_sec
            print(km_per_sweep)
            print(calculate_distance([self.y, self.x], self.leg_destination))
            if calculate_distance([self.y, self.x], self.leg_destination) < km_per_sweep:
                # Check if final leg completed
                if len(self.arrival) == self.leg + 2:
                    self.leg_destination = [airport_data["runway"]["start_lat"], airport_data["runway"]["start_long"]]
                # Check if at runway
                # elif len(self.arrival) > self.leg:
                    # at runway, initiate landing
                else:
                    # Set location to exact waypoint (helps with accuracy on next leg)
                    self.y, self.x = self.leg_destination
                    self.leg += 1

                    self.leg_destination = self.arrival[self.leg + 1][0]

                # Calculate new heading
                self.heading = calculate_bearing([self.y, self.x], self.leg_destination)

        # Calculate difference to lat and lon using km to cood conversions
        self.y += cos(radians(self.heading)) * (self.h / 110.574)
        self.x += sin(radians(self.heading)) * (
            self.h / (111.320 * cos(radians(self.y)))
        )
        self.label()

    def label(self):
        from main import scene, selected, label_sweep
        scene.label(self, selected, label_sweep)

    def change_altitude(self, altitude):
        self.target_altitude = altitude

    def show_route(self):
        from main import radar
        if self.arrival != None:
            radar.show_arrival(self.arrival)

    def hide_route(self):
        from main import radar
        radar.hide_arrival()
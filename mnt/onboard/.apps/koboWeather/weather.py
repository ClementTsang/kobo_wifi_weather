# -*- coding: utf-8 -*-

import urllib2
import pygame
import os

import json
import string
from datetime import date, datetime, timedelta
from subprocess import call

os.environ["SDL_NOMOUSE"] = "1"
print("Kobo Wifi weather forecast started.")


def index_error(error):
    print(error)
    print("Failed to fetch weather data.")
    print("Double check your config settings by running:")
    print(" cat /mnt/onboard/.apps/koboWeather/config")
    print("If the information is incorrect, re-set your config with:")
    print(" /mnt/onboard/.apps/koboWeather/set_config.sh")


def to_hex(color):
    hex_chars = "0123456789ABCDEF"
    return hex_chars[color / 16] + hex_chars[color % 16]


def convert_to_raw(surface):
    print("Converting image . . .")
    raw_img = ""
    for row in range(surface.get_height()):
        for col in range(surface.get_width()):
            color = surface.get_at((col, row))[0]
            raw_img += ("\\x" + to_hex(color)).decode("string_escape")
    with open("/tmp/img.raw", "wb") as f:
        f.write(raw_img)
    print("Image converted.")


def owm_icon_mapping():
    mapping = {}
    with open("owm_icon_mappings.txt", "r") as f:
        for line in f.readlines():
            splits = line.split(": ")
            if len(splits) == 2:
                owm_code = int(splits[0].strip().split("-")[-1])
                icon_name = splits[1].strip()
                mapping[owm_code] = "wi-{0}.png".format(icon_name)
    return mapping


def get_weather_data():
    print("Getting weather information . . .")

    try:
        with open("config", "r") as config:
            lat = config.readline().strip()
            lon = config.readline().strip()
            units = config.readline().strip()
            api_key = config.readline().strip()
    except IOError:
        print("\nCouldn't open config file.")
        print("Run the 'set_config.sh' script to set your config for the weather script.")
        return 1
    weather_link = "https://api.openweathermap.org/data/2.5/onecall?lat={0}&lon={1}&units={2}&exclude=minutely,hourly,alerts,current&appid={3}".format(
        lat, lon, units, api_key
    )
    weather_json = urllib2.urlopen(weather_link)
    weather_data = json.loads(weather_json.read())
    weather_json.close()

    unit_file = open("unit.txt", "r")
    unit = unit_file.read()
    unit_file.close()
    unit = unit.strip().upper()

    highs = ["{:.0f}".format(round(day["temp"]["max"])) for day in weather_data["daily"]]
    lows = ["{:.0f}".format(round(day["temp"]["min"])) for day in weather_data["daily"]]
    conditions = [string.capwords(day["weather"][0]["description"]) for day in weather_data["daily"]]

    now = datetime.now()
    day3 = now + timedelta(days=2)
    day4 = now + timedelta(days=3)
    day5 = now + timedelta(days=4)
    days = ["Today", "Tomorrow", day3.strftime("%A"), day4.strftime("%A"), day5.strftime("%A")]

    # images
    icon_map = owm_icon_mapping()
    img_dirs = ["icons/" + icon_map[day["weather"][0]["id"]] for day in weather_data["daily"]]

    display(days, highs, lows, conditions, img_dirs, unit)


def display(days, highs, lows, conditions, img_links, unit):

    print("Creating image . . .")

    pygame.font.init()

    white = (255, 255, 255)
    black = (0, 0, 0)
    gray = (125, 125, 125)

    screen = pygame.Surface((600, 800))
    screen.fill(white)

    update_font = pygame.font.Font("SF-Pro.ttf", 16)
    tiny_font = pygame.font.Font("SF-Pro.ttf", 18)
    small_font = pygame.font.Font("SF-Pro.ttf", 22)
    medium_font = pygame.font.Font("SF-Pro.ttf", 35)
    font = pygame.font.Font("SF-Pro.ttf", 40)
    title_font = pygame.font.Font("SF-Pro.ttf", 60)

    # Dividing lines
    pygame.draw.line(screen, gray, (10, 200), (590, 200))
    pygame.draw.line(screen, gray, (10, 400), (590, 400))
    pygame.draw.line(screen, gray, (200, 410), (200, 790))
    pygame.draw.line(screen, gray, (400, 410), (400, 790))

    # Today
    date = small_font.render(days[0], True, black, white)
    date_rect = date.get_rect()
    date_rect.topleft = 10, 15

    high = small_font.render("high: ", True, black, white)
    high_rect = high.get_rect()
    high_temp = title_font.render(highs[0], True, black, white)
    htemp_rect = high_temp.get_rect()
    high_rect.topleft = (50, 100)
    htemp_rect.topleft = high_rect.topright

    low = small_font.render("low: ", True, black, white)
    low_rect = low.get_rect()
    low_rect.topleft = (400, 100)
    low_temp = title_font.render(lows[0], True, black, white)
    ltemp_rect = low_temp.get_rect()
    ltemp_rect.topleft = low_rect.topright

    condition = font.render(conditions[0], True, black, white)
    con_rect = condition.get_rect()
    con_rect.centerx = 300
    con_rect.top = 5
    # Make sure words don't overlap
    if con_rect.left < date_rect.right:
        con_rect.left = date_rect.right

    image = pygame.image.load(img_links[0])
    image.set_colorkey((255, 255, 255))
    img_rect = image.get_rect()
    img_rect.center = (300, 135)
    degrees = tiny_font.render(unicode("°{0}".format(unit), "utf8"), True, black, white)

    screen.blit(condition, con_rect)
    screen.blit(high, high_rect)
    screen.blit(degrees, htemp_rect.topright)
    screen.blit(degrees, ltemp_rect.topright)
    screen.blit(high_temp, htemp_rect)
    screen.blit(low, low_rect)
    screen.blit(low_temp, ltemp_rect)
    screen.blit(image, img_rect)
    screen.blit(date, date_rect)

    # Tomorrow
    date = small_font.render(days[1], True, black, white)
    date_rect = date.get_rect()
    date_rect.topleft = 10, 210

    high = small_font.render("high: ", True, black, white)
    high_rect = high.get_rect()
    high_temp = title_font.render(highs[1], True, black, white)
    htemp_rect = high_temp.get_rect()
    high_rect.topleft = (50, 300)
    htemp_rect.topleft = high_rect.topright

    low = small_font.render("low: ", True, black, white)
    low_rect = low.get_rect()
    low_rect.topleft = (400, 300)
    low_temp = title_font.render(lows[1], True, black, white)
    ltemp_rect = low_temp.get_rect()
    ltemp_rect.topleft = low_rect.topright

    condition = font.render(conditions[1], True, black, white)
    con_rect = condition.get_rect()
    con_rect.centerx = 300
    con_rect.top = 210
    if con_rect.left < date_rect.right:
        con_rect.left = date_rect.right

    image = pygame.image.load(img_links[1])
    image.set_colorkey((255, 255, 255))
    img_rect = image.get_rect()
    img_rect.center = (300, 335)

    screen.blit(condition, con_rect)
    screen.blit(high, high_rect)
    screen.blit(degrees, htemp_rect.topright)
    screen.blit(degrees, ltemp_rect.topright)
    screen.blit(high_temp, htemp_rect)
    screen.blit(low, low_rect)
    screen.blit(low_temp, ltemp_rect)
    screen.blit(image, img_rect)
    screen.blit(date, date_rect)

    # Day 3
    date = small_font.render(days[2], True, black, white)
    date_rect = date.get_rect()
    date_rect.centerx = 100
    date_rect.top = 410

    high = small_font.render("high: ", True, black, white)
    high_rect = high.get_rect()
    high_temp = medium_font.render(highs[2], True, black, white)
    htemp_rect = high_temp.get_rect()
    high_rect.topright = (100, 630)
    htemp_rect.midleft = high_rect.midright

    low = small_font.render("low:  ", True, black, white)
    low_rect = low.get_rect()
    low_rect.topright = (100, 710)
    low_temp = medium_font.render(lows[2], True, black, white)
    ltemp_rect = low_temp.get_rect()
    ltemp_rect.midleft = low_rect.midright

    condition = tiny_font.render(conditions[2], True, black, white)
    con_rect = condition.get_rect()
    con_rect.centerx = 100
    con_rect.top = 450

    image = pygame.image.load(img_links[2])
    image.set_colorkey((255, 255, 255))
    img_rect = image.get_rect()
    img_rect.center = (100, 540)

    screen.blit(condition, con_rect)
    screen.blit(high, high_rect)
    screen.blit(degrees, htemp_rect.topright)
    screen.blit(degrees, ltemp_rect.topright)
    screen.blit(high_temp, htemp_rect)
    screen.blit(low, low_rect)
    screen.blit(low_temp, ltemp_rect)
    screen.blit(image, img_rect)
    screen.blit(date, date_rect)

    # Day 4
    date = small_font.render(days[3], True, black, white)
    date_rect = date.get_rect()
    date_rect.centerx = 300
    date_rect.top = 410

    high = small_font.render("high: ", True, black, white)
    high_rect = high.get_rect()
    high_temp = medium_font.render(highs[3], True, black, white)
    htemp_rect = high_temp.get_rect()
    high_rect.topright = (300, 630)
    htemp_rect.midleft = high_rect.midright

    low = small_font.render("low:  ", True, black, white)
    low_rect = low.get_rect()
    low_rect.topright = (300, 710)
    low_temp = medium_font.render(lows[3], True, black, white)
    ltemp_rect = low_temp.get_rect()
    ltemp_rect.midleft = low_rect.midright

    condition = tiny_font.render(conditions[3], True, black, white)
    con_rect = condition.get_rect()
    con_rect.centerx = 300
    con_rect.top = 450

    image = pygame.image.load(img_links[3])
    image.set_colorkey((255, 255, 255))
    img_rect = image.get_rect()
    img_rect.center = (300, 540)

    screen.blit(condition, con_rect)
    screen.blit(high, high_rect)
    screen.blit(degrees, htemp_rect.topright)
    screen.blit(degrees, ltemp_rect.topright)
    screen.blit(high_temp, htemp_rect)
    screen.blit(low, low_rect)
    screen.blit(low_temp, ltemp_rect)
    screen.blit(image, img_rect)
    screen.blit(date, date_rect)

    # Day 5
    date = small_font.render(days[4], True, black, white)
    date_rect = date.get_rect()
    date_rect.centerx = 500
    date_rect.top = 410

    high = small_font.render("high: ", True, black, white)
    high_rect = high.get_rect()
    high_temp = medium_font.render(highs[4], True, black, white)
    htemp_rect = high_temp.get_rect()
    high_rect.topright = (500, 630)
    htemp_rect.midleft = high_rect.midright

    low = small_font.render("low:  ", True, black, white)
    low_rect = low.get_rect()
    low_rect.topright = (500, 710)
    low_temp = medium_font.render(lows[4], True, black, white)
    ltemp_rect = low_temp.get_rect()
    ltemp_rect.midleft = low_rect.midright

    condition = tiny_font.render(conditions[4], True, black, white)
    con_rect = condition.get_rect()
    con_rect.centerx = 500
    con_rect.top = 450

    image = pygame.image.load(img_links[4])
    image.set_colorkey((255, 255, 255))
    img_rect = image.get_rect()
    img_rect.center = (500, 540)

    screen.blit(condition, con_rect)
    screen.blit(high, high_rect)
    screen.blit(degrees, htemp_rect.topright)
    screen.blit(degrees, ltemp_rect.topright)
    screen.blit(high_temp, htemp_rect)
    screen.blit(low, low_rect)
    screen.blit(low_temp, ltemp_rect)
    screen.blit(image, img_rect)
    screen.blit(date, date_rect)

    update_time = "Last updated at " + datetime.now().strftime("%-l:%M%P")
    last_update = update_font.render(update_time, True, gray, white)
    screen.blit(last_update, (5, 776))

    convert_to_raw(screen)
    call(["/mnt/onboard/.python/display_raw.sh"])


if __name__ == "__main__":
    get_weather_data()

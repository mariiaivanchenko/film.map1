"""MAP MODULE"""

import argparse
import os.path
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable 
from haversine import haversine
import folium
import time

parser = argparse.ArgumentParser()

parser.add_argument("year1", type = int)
parser.add_argument("latitude", type = float)
parser.add_argument("longtitude", type = float)
parser.add_argument("datasetpath", type = str)

args = parser.parse_args()

year1 = args.year1
latitude = args.latitude
longtitude = args.longtitude
path = args.datasetpath

def check(path: str, latitude: float, longtitude: float, year1: int) -> bool:
    """
    This function check input validation.
    """
    if os.path.isfile(path) is False:
        return "File doesn`t exist"
    if latitude < -90 or latitude > 90:
        return "Incorrect lattitude"
    if longtitude < -180 or longtitude > 180:
        return "Incorrect longtitude"
    if year1 <= 1860:
        return "There is no films created this year"
    if year1 >= 2023:
        return "There is no films created this year"
    return True

def read_file(file: str, year: int) -> list:
    """
    Read file, return file data.
    """
    with open(file, encoding= "utf-8") as files:
        data = files.readlines()[14:]
    result = []
    places = []
    for _, val in enumerate(data):
        if str(year) in val:
            place = val.split("\t")[-1].split("\n")[0]
            if "(" in place or place == "":
                place = val.split("\t")[-2].split("\n")[0]
            name = val.split(" ")[0]
            if place not in places:
                result.append((name, place))
            places.append(place)

    return result

def calculate(data: list, place: tuple) -> list:
    """
    Gets distances of each location by specific year.
    Returns a list of coordinates, location, film name and distance.
    """
    geolocator = Nominatim(user_agent="hehe_cat", timeout = 200)
    coords = []
    distance = []
    result = []
    for _, val in enumerate(data):
        for _, value in enumerate(val[1].split(",")):
            try:
                location = geolocator.geocode(value)
                if location is not None:
                    loc = (location.latitude, location.longitude)
                    dist = haversine(loc, place)
                    coords.append((loc,(value,val[0]),dist))
                    distance.append(dist)
                    break
            except GeocoderUnavailable:
                pass
    for _ in range(10):
        result.append(coords[distance.index(min(distance))])
        coords.pop(distance.index(min(distance)))
        distance.remove(min(distance))

    return result

def main(year: int, latitude: float,longtitude: float, file: str) -> list:
    """
    Return result.
    """
    if check(path, latitude, longtitude, year) is True:
        place = (latitude, longtitude)
        data = read_file(file, year)
        res = calculate(data, place)
        mapa(res,place)
        return res
    else:
        return "Invalid input"

def mapa(res: list, place: tuple):
    """
    This function creates map.
    """
    map = folium.Map(location=[place[0], place[1]], zoom_start = 5)

    folium.TileLayer("Stamen Toner",name = "Black And White").add_to(map)
    folium.TileLayer("Stamen Water Color",name = "Watercolor").add_to(map)
    folium.TileLayer("CartoDB Positron",name = "Grey").add_to(map)

    html= """<h4>Setting information:</h4>
    Place: {},<br>
    Film name: {}
    """
    base_layer = folium.FeatureGroup(name="Base")
    base_layer.add_child(folium.Marker(location =[place[0], place[1]], popup="Your location", icon=folium.Icon(color = "lightblue",icon="fa-thin fa-house", prefix = "fa")))

    second_layer = folium.FeatureGroup(name="Icons")
    for _, val in enumerate(res):
        iframe = folium.IFrame(html= html.format(val[1][0], val[1][1][1:-1]),width=200,height=100)
        second_layer.add_child(folium.Marker(location = [val[0][0], val[0][1]], popup = folium.Popup(iframe), icon=folium.Icon(color = "lightred",icon="fa-thin fa-star", prefix = "fa")))

    def color_creator(population):
        if population <= 1500:
            return "green"
        elif 1500 <= population <= 5000:
            return "yellow"
        else:
            return "red"
        
    third_layer = folium.FeatureGroup(name="Distancess")
    for _, val in enumerate(res):
        third_layer.add_child(folium.CircleMarker(location = [val[0][0], val[0][1]],color= None,  popup = folium.Popup(iframe), radius=20, fill_opacity=0.5, fill_color=color_creator(val[2])))


    map.add_child(base_layer)
    map.add_child(second_layer)
    map.add_child(third_layer)
    map.add_child(folium.LayerControl())
    map.save("FilmMap.html")

main(year1, latitude, longtitude, path)

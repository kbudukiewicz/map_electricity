from bazaConn import dataCountry
import itertools
import io
import os
import folium
import pandas as pd
from geopy.geocoders import Nominatim
import geopandas
import json
import numpy as np
from folium.plugins import TimeSliderChoropleth
from folium.plugins import MarkerCluster


# funkcja do inicjalizacji mapy
def initMap_coal():
    geolocator = Nominatim(user_agent='my_email@myserver.com')

    # tworzenie mapy
    m = folium.Map(location=[53, 16], tiles="Stamen Terrain", zoom_start=3)

    tooltip = 'Show information'

    water = dataCountry().getCoordinates("woda")
    water_group = MarkerCluster(name="Elektrownie wodne").add_to(m)
    for i in water:
        coor = [i[1], i[2]]
        popupText = str(i[0]) + ', elektrownia wodna, moc:' + str(i[3])
        water_group.add_child(
            folium.Marker(coor, icon=folium.Icon(color='darkgreen'), tooltip=tooltip, popup=popupText))

    wind = dataCountry().getCoordinates("wiatr")
    wind_group = MarkerCluster(name="Elektrownie wiatrowe").add_to(m)
    for i in wind:
        coor = [i[1], i[2]]
        popupText = str(i[0]) + ', elektrownia wiatrowa, moc:' + str(i[3])
        wind_group.add_child(folium.Marker(coor, icon=folium.Icon(color='lightgray'), tooltip=tooltip, popup=popupText))

    coal = dataCountry().getCoordinates("wegiel")
    coal_group = MarkerCluster(name="Elektrownie węglowe").add_to(m)
    for i in coal:
        coor = [i[1], i[2]]
        popupText = str(i[0]) + ', elektrownia weglowa, moc:' + str(i[3])
        coal_group.add_child(folium.Marker(coor, tooltip=tooltip, popup=popupText))

    solar = dataCountry().getCoordinates("slonce")
    solar_group = MarkerCluster(name="Elektrownie słoneczne").add_to(m)
    for i in solar:
        coor = [i[1], i[2]]
        popupText = str(i[0]) + ', elektrownia sloneczna, moc:' + str(i[3])
        solar_group.add_child(folium.Marker(coor, icon=folium.Icon(color='orange'), tooltip=tooltip, popup=popupText))

    atom = dataCountry().getCoordinates("atom")
    atom_group = MarkerCluster(name="Elektrownie atomowe").add_to(m)
    for i in atom:
        coor = [i[1], i[2]]
        popupText = str(i[0]) + ', elektrownia atomowa, moc:' + str(i[3])
        atom_group.add_child(folium.Marker(coor, icon=folium.Icon(color='pink'), tooltip=tooltip, popup=popupText))

    # path do json panstw
    json_path = r'countries.geo.json'

    countries = ['Austria', 'Belgia', 'Bulgaria', 'Chorwacja', 'Cypr', 'Czechy', 'Dania', 'Estonia', 'Finlandia',
                 'Francja', 'Grecja', 'Hiszpania', 'Holandia', 'Irlandia', 'Litwa', 'Luksemburg', 'Lotwa', 'Malta',
                 'Niemcy', 'Polska', 'Portugalia', 'Rumunia', 'Slowacja', 'Slowenia', 'Szwecja', 'Wegry', 'Wlochy']

    # pusta DataFrame, lata kolumny
    years = []
    years.extend([str(i) for i in range(1992, 2018)])
    index = range(len(countries))
    country_DF = pd.DataFrame(index=index, columns=years)

    # wypelnienie DataFrame i dodanie kolumny panstw
    for i in range(len(countries)):
        country_DF.loc[i] = dataCountry().table_get_info(countries[i], 'suma_zaniecz', '1992', '2017')

    with open(json_path) as geojson:
        country_json = json.load(geojson)

    denominations_json = []
    for index in range(len(country_json['features'])):
        denominations_json.append(country_json['features'][index]['properties']['name'])

    # ustawienie lat na float
    for year in years:
        country_DF[year] = country_DF[year].astype(float)

    # lata w jednej liscie w formie 1992 - 2018 i tak zapetlone
    lata = []
    for i in range(len(years)):
        lata.extend(list(itertools.repeat(years[i], len(denominations_json))))

    # zanieczyszczenia w jednej liscie ze zgadzajacymi datami jak wyzej
    zanieczyszczenie = []
    for i in range(27):
        zanieczyszczenie.extend(country_DF.loc[i])

    # DataFrame z kolumnami: Date, Country, Zanieczyszczenie
    data_all = pd.DataFrame()
    data_all.insert(0, 'Date', lata, True)
    data_all.insert(1, 'Country', denominations_json * len(years), True)
    data_all.insert(2, 'Zanieczyszczenie', zanieczyszczenie, True)

    # rok na datetime i ustawione na string
    data_all['Date'] = pd.to_datetime(data_all['Date'])

    # indeksy Date
    datetime_index = pd.DatetimeIndex(data_all['Date'])
    dt_index_epochs = datetime_index.astype(int) // 10 ** 9
    dt_index = dt_index_epochs.astype('U10')

    # slownik indeksowany nazwami obszarow
    id_dict = {denominations_json[0]: 0,
               denominations_json[1]: 1,
               denominations_json[2]: 2,
               denominations_json[3]: 3,
               denominations_json[4]: 4,
               denominations_json[5]: 5,
               denominations_json[6]: 6,
               denominations_json[7]: 7,
               denominations_json[8]: 8,
               denominations_json[9]: 9,
               denominations_json[10]: 10,
               denominations_json[11]: 11,
               denominations_json[12]: 12,
               denominations_json[13]: 13,
               denominations_json[14]: 14,
               denominations_json[15]: 15,
               denominations_json[16]: 16,
               denominations_json[17]: 17,
               denominations_json[18]: 18,
               denominations_json[19]: 19,
               denominations_json[20]: 20,
               denominations_json[21]: 21,
               denominations_json[22]: 22,
               denominations_json[23]: 23,
               denominations_json[24]: 24,
               denominations_json[25]: 25,
               denominations_json[26]: 26,
               }

    # tworzenie identyfikatora za pomoca powyzszego slownika
    data_all['Country_id'] = data_all['Country'].map(id_dict)
    # podzielenie zakresu na min i maks na 10 rownych czesci
    bins = np.linspace(min(data_all['Zanieczyszczenie']), max(data_all['Zanieczyszczenie']), 11)

    # ustawienie koloru dla podzialu
    data_all['Color'] = pd.cut(data_all['Zanieczyszczenie'], bins,
                               labels=['#FFEBEB', '#F8D2D4', '#F2B9BE', '#EBA1A8', '#E58892', '#DE6F7C', '#D85766',
                                       '#D13E50', '#CB253A', '#C50D24'], include_lowest=False)

    data_all['Country_id'] = data_all['Country_id'].astype(str)    # ustawienie Country_id na string
    data_all.insert(5, 'Date id', dt_index, True)       # dodanie Date id do DataFrame

    data_all = data_all[['Date id', 'Country_id', 'Color']]

    data_dict = {}
    for i in data_all['Country_id'].unique():
        data_dict[i] = {}
        for j in data_all[data_all['Country_id'] == i].set_index(['Country_id']).values:
            data_dict[i][j[0]] = {'color': j[1], 'opacity': 0.5}

    # wczytanie geojson, zakodowanie Country_id jako nazwy panstw, usuniecie niepotrzebnych kolumn
    ue_geojson = geopandas.read_file(json_path)
    ue_geojson['Country_id'] = ue_geojson['name'].map(id_dict)
    ue_geojson.drop(columns='name', inplace=True)
    ue_geojson.drop(columns='id', inplace=True)

    # TimeSliderChoropleth koncowy
    g = TimeSliderChoropleth(
        ue_geojson.set_index('Country_id').to_json(),
        styledict=data_dict
    ).add_to(m)

    folium.LayerControl().add_to(m)

    # zapisywanie danych z mapy
    data = io.BytesIO()
    m.save(data, close_file=False)

    return data

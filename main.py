import argparse
import os
from downloading_script import Downloader
from prepare_osm import DataBase
from search import Searcher

russia = {'central': 'https://download.geofabrik.de/russia/central-fed-district-latest.osm.bz2',
          'crimean': 'https://download.geofabrik.de/russia/crimean-fed-district-latest.osm.bz2',
          'far_eastern': 'https://download.geofabrik.de/russia/far-eastern-fed-district-latest.osm.bz2',
          'north_caucasus': 'https://download.geofabrik.de/russia/north-caucasus-fed-district-latest.osm.bz2',
          'northwestern': 'https://download.geofabrik.de/russia/northwestern-fed-district-latest.osm.bz2',
          'siberian': 'https://download.geofabrik.de/russia/siberian-fed-district-latest.osm.bz2',
          'south': 'https://download.geofabrik.de/russia/south-fed-district-latest.osm.bz2',
          'ural': 'https://download.geofabrik.de/russia/ural-fed-district-latest.osm.bz2',
          'volga': 'https://download.geofabrik.de/russia/volga-fed-district-latest.osm.bz2',
          'kaliningrad': 'https://download.geofabrik.de/russia/kaliningrad-latest.osm.bz2'}

region = {'kaliningrad': 'https://download.geofabrik.de/russia/kaliningrad-latest.osm.bz2'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--city', type=str, action='store')
    parser.add_argument('-s', '--street', type=str, action='store')
    parser.add_argument('-hn', '--house_number', type=str, action='store')
    parser.add_argument('-p', '--path', type=str, action='store',
                        help="path to save downloaded data")
    parser.add_argument('-r', '--regime', type=str, action='store',
                        choices=["region", "russia"])
    args = parser.parse_args().__dict__
    street = args['street']
    house_number = args['house_number']
    city = args['city']
    regime = args["regime"]
    path = args["path"]
    address = city + ", " + street + ", " + house_number
    if regime == "russia":
        links_to_download = russia
    else:
        links_to_download = region
    if not os.path.isdir(os.path.join(path, 'geodata')):
        Downloader.download_bz2(links_to_download, 'geodata')
    if not os.path.isdir(os.path.join(path, 'prepared')):
        for file in os.listdir(os.path.join(path, 'geodata')):
            if file.endswith(".txt"):
                print(f"preparing file: {os.path.join(path, 'geodata', file)}")
                db = DataBase(os.path.join(path, 'geodata', file),
                              os.path.join(path, 'prepared', file))
                s = Searcher(os.path.join(path, 'prepared', file))
    for file in os.listdir(os.path.join(path, 'prepared')):
        print("Created Searcher")
        s = Searcher(os.path.join(path, 'prepared', file))
        print(DataBase.return_json_address(args['city'], args['street'],
                                           args['house_number'], Searcher.get_median(s.search_nodes(address))))

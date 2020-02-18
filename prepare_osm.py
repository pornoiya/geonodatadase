import re
import os
from time import sleep
import argparse
import json
import sys


class DataBase:
    """Class which creates a file with useful for geocoder data
    file is a path to the raw file downloaded by Downloader
    path_to_save_db is a path to create file-db with only useful data
    """
    def __init__(self, file, path_to_save_db):
        os.makedirs('prepared', exist_ok=True)
        self.db_file = path_to_save_db
        self.file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
        self.total_size = os.path.getsize(self.file)
        self.current_size = 0
        self.fill_address_db(file)

    def fill_db_nodes(self, data_line):
        """Writes to db_file info about nodes and its coordinates"""
        if data_line:
            try:
                match = re.match(r'\s*<node id="(\d*).*lat="([\d.]*).*lon="([\d.]*).*/?>', data_line)
                node_ref = match.group(1)
                lat = match.group(2)
                lon = match.group(3)
                with open(self.db_file, 'a', encoding='utf8') as db:
                    self.current_size += len(data_line.encode(encoding="utf8"))
                    db.write(f"<({node_ref}): ({lat}, {lon})>" + os.linesep)
                    sleep(0.0001)
                    half_done = int(50 * self.current_size / self.total_size)
                    sys.stdout.write(f"\r[{'=' * half_done}{' ' * (50 - half_done)}] {2 * half_done}%")
                    sys.stdout.flush()
            except AttributeError:
                pass

    def fill_address_db(self, file):
        """Creates final database with only useful data"""
        tag_closed = True
        way_tag = ''
        with open(file, 'r', errors='ignore', encoding="utf8") as f:
            for line in f:
                try:
                    tag_opened = re.match(r'\s*<way id=".*>', line)
                    if tag_opened:
                        tag_closed = False
                    if re.match(r'\s*</way>.*', line):
                        try:
                            tag_closed = True
                            address = DataBase.cut_info(way_tag)[0]
                            refs = DataBase.cut_info(way_tag)[1]
                            with open(self.db_file, 'a', encoding='utf8') as db:
                                db.write(f"({address}): {refs}" + os.linesep)
                                self.current_size += len(line.encode(encoding="utf8"))
                                sleep(0.0001)
                                half_done = int(50 * self.current_size / self.total_size)
                                sys.stdout.write(f"\r[{'=' * half_done}{' ' * (50 - half_done)}] {2 * half_done}%")
                                sys.stdout.flush()
                            way_tag = ''
                        except IndexError:
                            pass
                    if not tag_closed:
                        way_tag += line
                    self.fill_db_nodes(line)
                except UnicodeError:
                    print(f"UNICODE ERROR OCCURRED{'!'*126}")
                    continue

    @staticmethod
    def cut_info(tag):
        """Cuts important info such as references, address
        out of <way>...</way> tag"""
        refs = re.findall(r'\s*<nd ref="(\d*)"/>', tag)
        house = re.findall(r'\s*<tag k="addr:housenumber" v="([/\-\w]*)"/>', tag)[0]
        city = re.findall(r'\s*<tag k="addr:city" v="(.*)"/>', tag)[0]
        street = re.findall(r'\s*<tag k="addr:street" v="(.*)"/>', tag)[0]
        addr = city + ', ' + street + ', ' + house
        return addr.lower(), refs

    @staticmethod
    def normalize_input(ip):
        """Makes entered address appropriated"""
        return ip.strip("\\/""''<>(){},.[]\n ").lower()

    @staticmethod
    def return_json_address(city, street, house, coords):
        return json.dumps({"address": {"city": city, "street": street,
                                       "house": house},
                           "coordinates": {"lat": coords[0],
                                           "lon": coords[1],
                                           "both": coords}})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, action='store', required=True,
                        help="path to file unzipped and downloaded by downloading_script")
    parser.add_argument('-s', '--save_path', type=str, action='store',  required=True,
                        help="path to file to store result")
    args = parser.parse_args().__dict__
    db = DataBase(args["path"], args["save_path"])

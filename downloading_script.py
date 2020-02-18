#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path
import bz2
import argparse
from urllib.request import urlretrieve


class Downloader:
    """Class which downloads a certain list of links .bz2 extension"""
    @staticmethod
    def download_bz2(links, folder_name):
        """Downloads russian database"""
        os.makedirs(folder_name, exist_ok=True)
        current_directory = os.path.dirname(os.path.realpath(__file__))
        for district in links.items():
            path_to_download = os.path.join(current_directory, folder_name)
            path_to_file = os.path.join(path_to_download, f"{district[0]}.bz2")
            urlretrieve(district[1], path_to_file)
            print("just have downloaded file")
            if not os.path.isfile(os.path.join(path_to_download, f"{district[0]}.txt")):
                Downloader.unzip_bz2_file(os.path.join(path_to_download, f"{district[0]}.bz2"),
                                          os.path.join(path_to_download, f"{district[0]}.txt"))

    @staticmethod
    def unzip_bz2_file(file_to_unzip, file_to_save):
        print("Unzipping")
        """Unzips bz2_file into file_to_save"""
        decompressed = bz2.open(file_to_unzip, 'rb')
        with open(file_to_save, 'a', encoding='utf-8') as file:
            for l in decompressed:
                try:
                    file.writelines(l.decode(encoding='utf8'))
                except UnicodeError:
                    continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', type=str, action='store',
                        help="folder to download geo data")
    args = parser.parse_args().__dict__
    region = {'kaliningrad': 'https://download.geofabrik.de/russia/kaliningrad-latest.osm.bz2'}
    Downloader.download_bz2(region, args["folder"])

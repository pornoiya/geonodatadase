import re
import argparse
import os
from prepare_osm import DataBase


class Searcher:
    """Class stat is responsible for searching address
    file_db is a data_file created by DataBase class
    """
    def __init__(self, file_db):
        self.file_db = file_db
        self.address_coordinates = {}

    def search_nodes(self, addr):
        """Searches necessary info about address in prepared file"""
        coords = []
        addr_refs = {}
        nodes_coords = {}
        with open(self.file_db, 'r', encoding='utf8') as db:
            for line in db:
                if re.match(r"\s*<\((.*)\):.*", line, re.DOTALL):
                    Searcher.string_ref_coord_normer(line, nodes_coords)
                elif re.match(r"\(.*\): \[.*\]", line, re.DOTALL):
                    Searcher.string_address_normalizer(line, addr_refs)
        refs = addr_refs.get(addr)
        if refs:
            [coords.append(nodes_coords.get(ref)) for ref in refs]
        return coords

    @staticmethod
    def string_address_normalizer(string, dict_to_save):
        """Gets rid of useless symbols in address string
        and saves it to dictionary"""
        addr, refs = string.split(":")
        refs_from_file = refs.strip("' ][\n").split(", ")
        refs_from_file = [ref.strip("'").replace("\n", "") for ref in refs_from_file]
        dict_to_save.update({addr.strip(")("): refs_from_file})

    @staticmethod
    def string_ref_coord_normer(string, dict_to_save):
        """Gets rid of useless symbols in ref_coord string
        and saves it ti dictionary"""
        ref, coords = string.split(":")
        ref = ref.strip("<)(")
        coords_normed = tuple([float(coord.strip(" )(>\n")) for coord in coords.strip(" )(>").split(", ")])
        dict_to_save.update({ref: coords_normed})

    @staticmethod
    def get_median(coords):
        """Returns a median value of list of coordinates"""
        lats = []
        lons = []
        for coord_tuple in coords:
            if coord_tuple:
                lat, lon = coord_tuple[0], coord_tuple[1]
                lats.append(float(lat))
                lons.append(float(lon))
        if lats and lons:
            return sum(lats) / len(lats), sum(lons) / len(lons)
        else:
            return 0, 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--city', type=str, action='store')
    parser.add_argument('-s', '--street', type=str, action='store')
    parser.add_argument('-hn', '--house_number', type=str, action='store')
    parser.add_argument('-p', '--path', type=str, action='store',
                        help="folder to the file prepared by prepare_osm")
    args = parser.parse_args().__dict__
    address = args['city'] + ", " + args['street'] + ", " + args['house_number']
    s = Searcher(args["path"])
    print(DataBase.return_json_address(args['city'], args['street'],
                                       args['house_number'], Searcher.get_median(s.search_nodes(address))))

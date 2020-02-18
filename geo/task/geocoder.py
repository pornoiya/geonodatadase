import re
import sqlite3
import os
import argparse

geo_objects = ['дом', 'улица', 'ул', 'проспект', 'проспектъ', 'переулок', 'бульвар', 'пр-т', 'тракт']


class DataBase:
    def __init__(self, file, database_name):
        self.conn = sqlite3.connect(database_name)
        self.cursor = self.conn.cursor()
        self.node_coordinates_name = 'node_coordinates'
        self.addr_node_name = 'addr_node_table'
        self.dict_node_coord = {}
        self.dict_addr_node = {}
        self.addr_node = ''
        #self.file = file
        self.file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
        if (f'{self.addr_node_name}',) not in self.get_tables_in_db():
            self.create_table_address_db()
            self.fill_address_db(self.file)
        elif (f'{self.node_coordinates_name}',) not in self.get_tables_in_db():
            self.create_table_node_coord()
            self.fill_db_nodes()

    def get_tables_in_db(self):
        self.cursor.execute('SELECT name from sqlite_master where type= "table"')
        return self.cursor.fetchall()

    def create_table_node_coord(self):
        try:
            self.cursor.execute(f"""CREATE TABLE {self.node_coordinates_name}
                              (node_ref integer, lat text, lon text)""")
        except sqlite3.OperationalError:
            pass

    def create_table_address_db(self):
        try:
            self.cursor.execute(f"""CREATE TABLE {self.addr_node_name}
                              (address text, nodes text)""")
        except sqlite3.OperationalError:
            pass

    def fill_db_nodes(self):
        with open(self.file, 'r', errors='ignore', encoding="utf8") as f:
            try:
                for data_line in f:
                    try:
                        match = re.match(r'\s*<node id="(\d*).*lat="([\d.]*).*lon="([\d.]*).*/>', data_line)
                        node_ref = match.group(1)
                        lat = match.group(2)
                        lon = match.group(3)
                        table = self.node_coordinates_name
                        self.cursor.execute(f"INSERT INTO {table} VALUES('{node_ref}', '{lat}', '{lon}')")
                        self.conn.commit()
                        self.dict_node_coord.update({node_ref: (lat, lon)})
                    except AttributeError:
                        continue
            except UnicodeDecodeError:
                pass

    def fill_address_db(self, file):
        with open(file, 'r', errors='ignore', encoding="utf8") as f:
            tag_closed = True
            way_tags = {}
            way_tag = ''
            for line in f:
                try:
                    tag_opened = re.match(r'\s*<way id=".*>', line)
                    if tag_opened:
                        tag_closed = False
                    if re.match(r'\s*</way>', line):
                        try:
                            tag_closed = True
                            address = DataBase.cut_info(way_tag)[0]
                            refs = ', '.join(DataBase.cut_info(way_tag)[1])
                            self.cursor.execute(f"INSERT INTO {self.addr_node_name} VALUES('{address}', '{refs}')")
                            self.conn.commit()
                            way_tag = ''
                        except IndexError:
                            pass
                    if not tag_closed:
                        way_tag += line
                except UnicodeError:
                    print(f"UNICODE ERROR OCCURRED")
                    continue
            return way_tags

    @staticmethod
    def cut_info(tag):
        refs = re.findall(r'\s*<nd ref="(\d*)"/>', tag)
        house_number = re.findall(r'\s*<tag k="addr:housenumber" v="([/\-\w]*)"/>', tag)[0]
        city = re.findall(r'\s*<tag k="addr:city" v="(\w*)"/>', tag)[0]
        street = re.findall(r'\s*<tag k="addr:street" v="([\s\w-]*)"/>', tag)[0]
        addr = city + ', ' + street + ', ' + house_number
        return addr.lower(), refs

    @staticmethod
    def normalize_input(ip):
        ip.strip("\\/""''<>(){},.[]\n ")
        splited = ip.lower().split()
        for part in splited:
            if part in geo_objects:
                ip.replace(part, "")
        return '%' + '%'.join(ip.lower().split()) + '%'

    def get_coordinates(self, nodes):
        coords = []
        for node in nodes:
            self.cursor.execute(f"SELECT * FROM {self.node_coordinates_name} WHERE node_ref ={int(node)}")
            reply = self.cursor.fetchone()
            if reply:
                coords.append((reply[1], reply[2]))
        return coords

    def drop_table(self, table_name):
        self.cursor.execute(f"DROP TABLE {table_name}")

    @staticmethod
    def get_median(coords):
        lats = []
        lons = []
        for coord_tuple in coords:
            lat, lon = coord_tuple
            lats.append(float(lat))
            lons.append(float(lon))
        if lats and lons:
            return sum(lats) / len(lats), sum(lons) / len(lons)
        else:
            return 0, 0


if __name__ == '__main__':
    """
    working example: ip = калининград, улица канта, 1
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, action='store', default='калининград, улица канта, 1')
    parser.add_argument('-p', '--path', type=str, action='store',
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site.txt'))

    args = parser.parse_args().__dict__
    ip = args['address']
    path = args['path']
    db = DataBase(path, 'Geo.db')
    tables_in_db = db.get_tables_in_db()
    req = db.normalize_input(ip)
    db.cursor.execute(f"SELECT * FROM {db.addr_node_name} WHERE address LIKE '{req}'")
    reply = db.cursor.fetchone()
    if reply:
        nodes = reply[1].split(', ')
        coordinates = db.get_coordinates(nodes)
        print(f"full address: {reply[0]}")
        print(DataBase.get_median(coordinates))


import unittest
import search
import os
from downloading_script import Downloader
from prepare_osm import DataBase
import main


class TestPreparing(unittest.TestCase):
    def test_normalizing_input(self):
        normed = DataBase.normalize_input("</NY, Houston avenue, 12.//")
        self.assertEqual(normed, "ny, houston avenue, 12")

    def test_skipping_new_line(self):
        normed = DataBase.normalize_input("</NY, Houston avenue, 12.//\n")
        self.assertEqual(normed, "ny, houston avenue, 12")

    def test_tuple_to_list_json(self):
        exp = "{\"address\": {\"city\": \"kgrad\", \"street\": \"kanta\", \"house\": \"1\"}," \
              " \"coordinates\": {\"lat\": 1.0, \"lon\": 2.0, \"both\": [1.0, 2.0]}}"
        self.assertEqual(DataBase.return_json_address("kgrad", "kanta", "1", (1.0, 2.0)), exp)

    def test__json(self):
        exp = "{\"address\": {\"city\": \"kgrad\", \"street\": \"kanta\", \"house\": \"1\"}," \
              " \"coordinates\": {\"lat\": 1.0, \"lon\": 2.0, \"both\": [1.0, 2.0]}}"
        self.assertEqual(DataBase.return_json_address("kgrad", "kanta", "1", [1.0, 2.0]), exp)

    def test_finding_address(self):
        test_string = """
          <way id="102650050" version="4" timestamp="2016-10-22T22:54:55Z">
            <nd ref="1185535609"/>
            <nd ref="1185535662"/>
            <nd ref="1185535654"/>
            <nd ref="1185535647"/>
            <nd ref="1185535609"/>
            <tag k="name" v="вилла Яффа"/>
            <tag k="building" v="yes"/>
            <tag k="addr:city" v="Калининград"/>
            <tag k="addr:street" v="улица Кутузова"/>
            <tag k="addr:housename" v="вилла Яффа"/>
            <tag k="addr:housenumber" v="10"/>
          </way>
        """
        address = DataBase.cut_info(test_string)[0]
        self.assertEqual(address, "калининград, улица кутузова, 10")

    def test_finding_node_refs(self):
        test_string = """
        <way id="102650050" version="4" timestamp="2016-10-22T22:54:55Z">
            <nd ref="1185535609"/>
            <nd ref="1185535662"/>
            <nd ref="1185535654"/>
            <nd ref="1185535647"/>
            <nd ref="1185535609"/>
            <tag k="name" v="вилла Яффа"/>
            <tag k="building" v="yes"/>
            <tag k="addr:city" v="Калининград"/>
            <tag k="addr:street" v="улица Кутузова"/>
            <tag k="addr:housename" v="вилла Яффа"/>
            <tag k="addr:housenumber" v="10"/>
          </way>
        """
        actual = DataBase.cut_info(test_string)[1]
        self.assertListEqual(actual, ["1185535609", "1185535662", "1185535654", "1185535647", "1185535609"])


class TestSearching(unittest.TestCase):
    def test_main_module(self):
        exp = ['central', 'crimean', 'far_eastern', 'north_caucasus',
               'northwestern', 'siberian', 'south', 'ural', 'volga', 'kaliningrad']
        act = [item[0] for item in main.russia.items()]
        self.assertEqual(exp, act)

    def test_initializing(self):
        p = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'filth.txt.bz2')
        s = search.Searcher(p)
        self.assertEqual(s.file_db, p)
        self.assertDictEqual(s.address_coordinates, {})

    def test_searching(self):
        f = os.path.join(os.getcwd(), "testing_to_prepare.txt")
        srchr = search.Searcher(f)
        adr = "липово, набережная улица, 30"
        exp = [(54.8199454, 18.3544725), (54.8216088, 18.351938), (54.8223243, 18.3508078),
               (54.8231284, 18.349651), (54.8256473, 18.3478349), (54.8239951, 18.3491378)]
        self.assertEqual(list(filter(None, srchr.search_nodes(adr))), exp)

    def test_getting_median_value(self):
        values = [(0, 1), (20, 15), (4, 8), (16, 0)]
        median = search.Searcher.get_median(values)
        self.assertAlmostEqual(median, (10.0, 6.0))

    def test_median_value_no_coordinates(self):
        values = ()
        self.assertEqual((0, 0), search.Searcher.get_median(values))

    def test_string_address_normalizer(self):
        str_to_norm = "(липово, набережная улица, 30): ['24933255', " \
                      "'24933258', '2204740869', '24933266', '24933275', " \
                      "'2204740743', '2204740708', '2204740910', '2204740852'," \
                      " '2204740621', '2204740648', '24933289', '24933276', " \
                      "'2204740855', '2204740652', '2204740776', '2204740789', " \
                      "'2204740636', '2204740813', '2204740687', '2204740601', " \
                      "'2204740695', '2204740743', '2204740793', '6364342746', " \
                      "'2204740853', '2204740796', '2204740761', '2204740857', " \
                      "'2204740773', '2204740721', '2204740726', '2204740646', " \
                      "'2204740749', '2204740848', '2204740900', '2204740784', " \
                      "'2204740843', '2204740836', '2204740838', '2204740593', " \
                      "'1081662492', '2204740845', '1467598110', '1081662580', " \
                      "'1081662532', '2204740623', '2204740737', '2204740735', " \
                      "'2204740898', '2204740623']"
        exp_list = ['24933255', '24933258', '2204740869', '24933266', '24933275',
                    '2204740743', '2204740708', '2204740910', '2204740852',
                    '2204740621', '2204740648', '24933289', '24933276',
                    '2204740855', '2204740652', '2204740776', '2204740789',
                    '2204740636', '2204740813', '2204740687', '2204740601', '2204740695',
                    '2204740743', '2204740793', '6364342746', '2204740853', '2204740796',
                    '2204740761', '2204740857', '2204740773', '2204740721', '2204740726',
                    '2204740646', '2204740749', '2204740848', '2204740900', '2204740784',
                    '2204740843', '2204740836', '2204740838', '2204740593', '1081662492',
                    '2204740845', '1467598110', '1081662580', '1081662532', '2204740623',
                    '2204740737', '2204740735', '2204740898', '2204740623']
        dictionary = {}
        search.Searcher.string_address_normalizer(str_to_norm, dictionary)
        self.assertListEqual(dictionary.get("липово, набережная улица, 30"), exp_list)

    def test_string_ref_normer(self):
        str_test = "<(24933255): (54.8199454, 18.3544725)>"
        dict_test = {}
        search.Searcher.string_ref_coord_normer(str_test, dict_test)
        self.assertTupleEqual(dict_test.get("24933255"), (54.8199454, 18.3544725))


class TestDownloader(unittest.TestCase):
    def test_unzipping_file(self):
        p = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'filth.txt.bz2')
        s = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'filth.txt')
        if not os.path.exists(s):
            Downloader.unzip_bz2_file(p, s)
        exp = """«Дерьмо» — роман Ирвина Уэлша, выпущенный в 1998 году.\n
Роман описывает расследование убийства чернокожего юноши, проводимое полицейским Брюсом Робертсоном.\n
Сюжет\n
Главных героев в книге два: Брюс Робертсон и глист, живущий в его кишечнике, от имени которого также\n
ведется повествование. Брюс — циничный, расчётливый, беспринципный и продажный полицейский, неразборчивый\n
в половых связях и регулярно употребляющий наркотики, который стремится заполучить вакантную должность\n
детектива-инспектора. Для устранения возможных конкурентов он использует любые методы. Попутно он расследует\n
убийство чернокожего юноши."""
        with open(s, 'r', encoding="utf8") as file:
            act = file.read()
        self.assertEqual(act, exp)

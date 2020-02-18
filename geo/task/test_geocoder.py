import unittest
import os
import geocoder as geo
import re


class TestNormalizationInput(unittest.TestCase):
    EXPECTED = '%улица%мамина-сибиряка,%1%'

    def test_redundant_symbols_skipping(self):
        act = geo.DataBase.normalize_input('улица Мамина-Сибиряка, 1')
        self.assertEqual(act, TestNormalizationInput.EXPECTED)

    def test_lowercase(self):
        act = geo.DataBase.normalize_input('УЛИЦА МАМИНА-СИБИРЯКА, 1')
        self.assertEqual(TestNormalizationInput.EXPECTED, act)

    def test_recognition_complex_data(self):
        act = geo.DataBase.normalize_input('улица Мамина-Сибиряка 46Б/4')
        self.assertEqual(act, '%улица%мамина-сибиряка%46б/4%')

    def test_commas(self):
        act = geo.DataBase.normalize_input('улица, Красноармейская, 22')
        self.assertEqual(act, '%улица,%красноармейская,%22%')


class TestDataBaseInteraction(unittest.TestCase):
    db = geo.DataBase(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site.txt'), 'Test.db')

    def test_getting_tables_in_db(self):
        actual = TestDataBaseInteraction.db.get_tables_in_db()
        self.assertTupleEqual(tuple(actual), ((TestDataBaseInteraction.db.addr_node_name, ),
                                              (TestDataBaseInteraction.db.node_coordinates_name, )))

    def test_dropping_existing_table(self):
        TestDataBaseInteraction.db.cursor.execute("CREATE TABLE testing_table (field text)")
        tables_after_creating = set(TestDataBaseInteraction.db.get_tables_in_db())
        TestDataBaseInteraction.db.drop_table("testing_table")
        tables_after_deleting = set(TestDataBaseInteraction.db.get_tables_in_db())
        diff = tables_after_creating.difference(tables_after_deleting)
        self.assertTrue(diff, ('testing_table',))


    def test_cutting_info(self):
        with open(TestDataBaseInteraction.db.file, 'r', encoding='utf8') as f:
            tags = re.findall(r'\s*<way id=.*?</way>', f.read(), re.DOTALL)
            res = [geo.DataBase.cut_info(tag) for tag in tags]
            exp = [('калининград, улица щепкина, 22',
                    ['1474012880', '1474012905', '1474012895', '1474012876', '1474012880']),
                   ('калининград, улица аллея смелых, 156',
                    ['1472926633', '1472926618', '1472926555', '1472926557', '1472926633'])]
            self.assertEqual(res, exp)

    def test_getting_median_value(self):
        coordinates = [(14.01, 13), (15.23, 0.5), (24.76, 4.5)]
        self.assertTupleEqual(geo.DataBase.get_median(coordinates), (18.0, 6.0))

    def test_getting_median_value_big(self):
        coordinates = [(14.01, 13), (15.23, 0.5), (24.76, 4.5)]*6
        self.assertAlmostEqual(18.0, geo.DataBase.get_median(coordinates)[0])


if __name__ == '__main__':
    unittest.main()

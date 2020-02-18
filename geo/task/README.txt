Приложение «Геокодер»
Версия 2.1
@author: Кихтенко Татьяна @leninanadejda@gmail.com

Описание
Вход: адрес в свободной форме
Выход: координаты и полный адрес
Требования
Python версии не ниже 3.6
Состав:
• Запуск программы: main.py
• Скрипт, скачивающий файлы: downloading_script.py
• Скрипт, формирующий файл-базу данных: prepare_osm.py
• Скрипт, осуществляющий поиск: search.py
• Тесты: test_geocoder.py

_____________________________________________________
Для каждого скрипта реализован консольный режим.
Примеры запуска:
• downloading_script:
    >>py downloading_script.py -f "folder_to_download_zip"
    >>py downloading_script.py --folder "folder_to_download_zip"
• prepare_osm:
    >>py prepare_osm.py -p "path_to_downloaded_zip" -s "path_to_store_prepared_info"
• search:
    >>py search.py -c "калининград" -s "улица канта" -hn 1 -p "C:\Users\lactn\PycharmProjects\untitled\geo\geo3\geo\tsk
      \prepared\kaliningrad.txt"

_____________________________________________________

Ключи:
-s улица
-c город
-hn номер дома
-p путь, где вы хотите развернуть действо геокодирования
-r режим. есть два режима russia и region. region парсит только
    калининградскую область (она самая маленькая) для тестового запуска,
    russia -- парсинг всей россии.

Пример запуска:
main.py -c калининград -s "улица канта" -hn 1 -p C:\\Users\\lactn\\PycharmProjects\\untitled\\geo\\geo3\\geo -r region

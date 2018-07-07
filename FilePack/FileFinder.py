from FilePack import ReadFile, Crypt
import os
import platform
from datetime import datetime, timedelta, timezone
from pathlib import Path


def days_from_modifed(s):  # Подсчет дней с последней модификации файла
    path = Path(s)
    statResult = path.stat()
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    modified = epoch + timedelta(seconds=statResult.st_mtime)
    return (datetime.today().utcnow().date() - modified.date()).days


def find(data):
    """
        Поиск полного пути до файла.
        :param name: Имя целевого файла
        :param path: Коренной путь поиска
        :return: путь
    """
    root_start = '/' # Стартовый корень от которого мы начинаем поиск.
    flag = False
    if platform.system() == 'Windows':
        root_start = 'C:\\'
        flag = True

    result = dict()  # Результат нашей проверки.

    for root, dirs, files in os.walk(root_start):
        for file in files:
            file = os.path.join(root, file)

            if not os.access(file, os.R_OK) and flag:  # Файлы, которые нельзя, прочесть будут пропущены !!!
                continue

            if not os.path.isfile(file) or os.path.isdir(file): # Является ли file  файлом или директорией.
                continue

            statinfo = os.stat(file)
            file_size = statinfo.st_size  # Размер файла

            if days_from_modifed(
                    file) > 10:  # Сколько времени прошло с последнего изменения файла. Если более 10 дней, то пропустим
                continue

            path = os.path.join(root, file)
            file_text = ReadFile.file_get_contents(file)  # Содержимое файла

            for t in data:  # Обход данных из бюллетени
                if t[1] == file_size:
                    if t[2]['MD5'] == Crypt.crypt_md5(file_text):
                        if t[2]['SHA1'] == Crypt.crypt_sha1(file_text):
                            if t[2]['SHA256'] == Crypt.crypt_sha256(file_text):
                                result[file] = path

    return result


"""
def find_all(name, path):
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result
"""
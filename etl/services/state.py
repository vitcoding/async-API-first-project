import json
from abc import abstractmethod
from typing import Any, Dict

from pydantic.dataclasses import dataclass
from redis import Redis

from services.base import Config

import json
import os
from abc import abstractmethod
from typing import Any, Dict

from pydantic.dataclasses import dataclass


@dataclass(config=Config)
class BaseStorage(object):
    @abstractmethod
    def save_state(self, state: Dict) -> None:
        """
        Сохраняет состояние в хранилище.

        :param state: Словарь, представляющий состояние для сохранения.
        """
        ...

    @abstractmethod
    def retrieve_state(self) -> Dict:
        """
        Извлекает состояние из хранилища.

        :return: Словарь, представляющий извлеченное состояние.
        """
        ...


@dataclass
class JsonStorage(BaseStorage):
    file_path: str

    def save_state(self, state: Dict) -> None:
        """
        Сохраняет состояние в JSON-файл.

        :param state: Словарь, представляющий состояние для сохранения.
        """
        with open(self.file_path, 'w') as file:
            json.dump(state, file, default=str)

    def retrieve_state(self) -> Dict:
        """
        Извлекает состояние из JSON-файла.

        :return: Словарь, представляющий извлеченное состояние, или пустой словарь, если данных нет.
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        return {}


@dataclass(config=Config)
class State(object):
    storage: BaseStorage

    def __post_init__(self):
        """
        Инициализирует состояние и загружает данные из хранилища.
        """
        self.data = self.storage.retrieve_state()

    def write_state(self, key: str, value: Any) -> None:
        """
        Записывает значение в состояние под заданным ключом.

        :param key: Ключ, под которым будет храниться значение.
        :param value: Значение для сохранения.
        """
        self.data[key] = value
        self.storage.save_state(self.data)

    def read_state(self, key: str, default: Any = None) -> Any:
        """
        Читает значение из состояния по заданному ключу.

        :param key: Ключ, по которому будет извлечено значение.
        :param default: Значение по умолчанию, если ключ не найден.
        :return: Значение, соответствующее ключу, или значение по умолчанию.
        """
        return self.data.get(key, default)

import abc
import json
import os
from typing import Any, Dict


class BaseStorage(abc.ABC):
    """Абстрактное хранилище состояния.

    Позволяет сохранять и получать состояние.
    Способ хранения состояния может варьироваться в зависимости
    от итоговой реализации. Например, можно хранить информацию
    в базе данных или в распределённом файловом хранилище.
    """

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Абстарктый метод сохранения состояния в хранилище."""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Абстрактный метод получения состояния из хранилища."""
        pass


class JsonFileStorage(BaseStorage):
    """Реализация хранилища, использующего локальный файл.

    Формат хранения: JSON
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        """Метод сохранения состояния в хранилище."""

        with open(self.file_path, mode="w", encoding="utf-8") as json_file:
            json.dump(state, json_file, indent=2)

    def retrieve_state(self) -> Dict[str, Any]:
        """Метод получения состояния из хранилища."""

        dir_path = "/".join((self.file_path).split("/")[:-1])
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        try:
            with open(self.file_path, mode="r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)
                return json_data
        except Exception:
            return {}


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Метод установки состояния для определённого ключа."""

        data = self.storage.retrieve_state()
        data[key] = value
        self.storage.save_state(data)

    def get_state(self, key: str) -> Any:
        """Метод получения состояния по определённому ключу."""

        data = self.storage.retrieve_state()
        state = data.get(key, None)
        return state

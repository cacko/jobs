from typing import Optional
import requests
from jobs.config import app_config
from jobs.masha.models import Token, ENDPOINT


class Skills:

    __result: Optional[list[Token]] = None

    def __init__(self, text: str) -> None:
        self.__text = text

    @property
    def result(self) -> list[Token]:
        try:
            assert self.__result
            return self.__result
        except AssertionError:
            data = {"message": self.__text}
            url = f"http://{app_config.masha.host}:{app_config.masha.port}/{ENDPOINT.SKILLS}"
            res = requests.post(url, json=data)
            self.__result = [Token(**t) for t in res.json().get("response", [])]
            return self.__result

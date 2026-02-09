# parsers/base_parser.py
from abc import ABC, abstractmethod
from typing import List
from pipeline.raw_event import RawEvent


class BaseParser(ABC):

    @abstractmethod
    def parse(self) -> List[RawEvent]:
        """
        Parse raw artefacts and return a list of RawEvent objects.
        """
        pass

# parsers/base_parser.py

from abc import ABC, abstractmethod
from typing import List
from pipeline.raw_event import RawEvent


class BaseParser(ABC):
    """
    Abstract base class for all artefact parsers.
    Ensures consistent parsing interface.
    """

    @abstractmethod
    def parse(self) -> List[RawEvent]:
        """Return a list of RawEvent objects."""
        raise NotImplementedError
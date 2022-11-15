from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from notion.objects import RichText, User


@dataclass
class Property(ABC):
    name: str
    value: Any

    @abstractmethod
    def to_dict(self) -> Dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, property_dict: Dict) -> Property:
        pass

    def update(self, value: Any) -> None:
        self.value = value


@dataclass
class SelectProperty(Property):
    value: Optional[str]

    def to_dict(self) -> Dict:
        return {
            "select": {"name": self.value}
        }

    @classmethod
    def from_dict(cls, property_dict: Dict) -> SelectProperty:
        property_name = list(property_dict.keys())[0]
        property_select = property_dict[property_name]["select"]
        property_value = (property_select["name"]
                          if property_select is not None else None)
        return cls(name=property_name, value=property_value)


@dataclass
class MultiSelectProperty(Property):
    value: List[str]

    def to_dict(self) -> Dict:
        return {
            "multi_select": [
                {"name": item}
                for item in self.value
            ]
        }

    @classmethod
    def from_dict(cls, property_dict: Dict) -> MultiSelectProperty:
        property_name = list(property_dict.keys())[0]
        property_value = [item["name"]
                          for item in property_dict[property_name]["multi_select"]]
        return cls(name=property_name, value=property_value)


@dataclass
class TextProperty(Property):
    value: List[RichText]

    def to_dict(self) -> Dict:
        return {"rich_text": [rich_text.to_dict() for rich_text in self.value]}

    @classmethod
    def from_dict(cls, property_dict: Dict) -> TextProperty:
        property_name = list(property_dict.keys())[0]
        property_text_list = property_dict[property_name]["rich_text"]
        if property_text_list:
            property_value = [RichText.from_dict(object_dict=property_text)
                              for property_text in property_text_list]
        else:
            property_value = []
        return cls(name=property_name, value=property_value)

    def update(self, value: List[RichText]) -> None:
        self.value = value


@dataclass
class TitleProperty(Property):
    value: str

    def to_dict(self) -> Dict:
        return {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": self.value
                    }
                }
            ]
        }

    @classmethod
    def from_dict(cls, property_dict: Dict) -> TitleProperty:
        property_name = list(property_dict.keys())[0]
        property_text_list = property_dict[property_name]["title"]
        if property_text_list:
            property_value = property_text_list[0]["text"]["content"]
        else:
            property_value = ""
        return cls(name=property_name, value=property_value)


@dataclass
class PeopleProperty(Property):
    value: List[User]

    def to_dict(self) -> Dict:
        return {
            "people": [
                people.to_dict()
                for people in self.value
            ]
        }

    @classmethod
    def from_dict(cls, property_dict: Dict) -> PeopleProperty:
        property_name = list(property_dict.keys())[0]
        property_value = [User.from_dict(object_dict=people)
                          for people in property_dict[property_name]["people"]]
        return cls(name=property_name, value=property_value)


@dataclass
class FormulaProperty(Property):
    value: Any
    type: str

    def to_dict(self) -> Dict:
        return {
            self.type: self.value
        }

    @classmethod
    def from_dict(cls, property_dict: Dict) -> FormulaProperty:
        property_name = list(property_dict.keys())[0]
        property_type = property_dict[property_name]["formula"]["type"]
        property_value = property_dict[property_name]["formula"][property_type]
        return cls(name=property_name, value=property_value, type=property_type)


PROPERTY_TYPE_TO_SUBCLASS = {
    "select": SelectProperty,
    "multi_select": MultiSelectProperty,
    "rich_text": TextProperty,
    "title": TitleProperty,
    "people": PeopleProperty,
    "formula": FormulaProperty
}

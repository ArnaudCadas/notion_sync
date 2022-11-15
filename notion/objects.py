from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Union


@dataclass
class Page:
    id: str

    def to_dict(self) -> str:
        return self.id

    @classmethod
    def from_dict(cls, object_dict: str) -> Page:
        page_id = object_dict
        return cls(id=page_id)

    def update(self, page_id: str) -> None:
        self.id = page_id

    def __str__(self):
        return self.id


@dataclass
class User:
    id: str
    name: str

    def to_dict(self) -> Dict:
        return {
            "object": "user",
            "id": self.id
        }

    @classmethod
    def from_dict(cls, object_dict: Dict) -> User:
        user_id = object_dict["id"]
        user_name = object_dict["name"]
        return cls(id=user_id, name=user_name)

    def update(self, user_id: str, user_name: str) -> None:
        self.id = user_id
        self.name = user_name

    def __str__(self):
        return self.name


MentionType = Union[Page, User]
MENTION_TYPE_TO_CLASS = {
    "page": Page,
    "user": User
}


@dataclass
class Mention:
    object: MentionType

    def to_dict(self) -> Dict:
        object_type = [
            type_string
            for type_string, type_class in MENTION_TYPE_TO_CLASS.items()
            if isinstance(self.object, type_class)
        ][0]
        return {
            "type": object_type,
            object_type: self.object.to_dict(),
        }

    @classmethod
    def from_dict(cls, object_dict: Dict) -> Mention:
        object_type = object_dict["type"]
        object_class = MENTION_TYPE_TO_CLASS.get(object_type, None)
        if object_class is None:
            raise NotImplementedError(
                f"The {object_type} object type is not implemented.")
        object_value = object_dict[object_type]
        object_instance = object_class.from_dict(object_dict=object_value)
        return cls(object=object_instance)

    def update(self, new_object: MentionType) -> None:
        self.object = new_object

    def __str__(self):
        return f"{self.object}"


@dataclass
class Text:
    content: str
    link: str = None

    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "link": {"url": self.link}
            if self.link is not None else None
        }

    @classmethod
    def from_dict(cls, object_dict: Dict) -> Text:
        text_content = object_dict["content"]
        text_link = object_dict["link"]
        link = text_link["url"] if text_link is not None else None
        return cls(content=text_content, link=link)

    def update(self, content: str, link: str = None) -> None:
        self.content = content
        self.link = link

    def __str__(self):
        return self.content


RichTextType = Union[Text, Mention]
RICH_TEXT_TYPE_TO_CLASS = {
    "text": Text,
    "mention": Mention
}


@dataclass
class RichText:
    object: RichTextType
    plain_text: str
    href: str = None

    def to_dict(self) -> Dict:
        object_type = [
            type_string
            for type_string, type_class in RICH_TEXT_TYPE_TO_CLASS.items()
            if isinstance(self.object, type_class)
        ][0]
        return {
            "type": object_type,
            object_type: self.object.to_dict(),
            "plain_text": self.plain_text,
            "href": self.href
        }

    @classmethod
    def from_dict(cls, object_dict: Dict) -> RichText:
        object_type = object_dict["type"]
        object_class = RICH_TEXT_TYPE_TO_CLASS.get(object_type, None)
        if object_class is None:
            raise NotImplementedError(
                f"The {object_type} object type is not implemented.")
        object_value = object_dict[object_type]
        object_instance = object_class.from_dict(object_dict=object_value)
        plain_text = object_dict["plain_text"]
        href = object_dict["href"]
        return cls(object=object_instance, plain_text=plain_text, href=href)

    def update(self, new_object: RichTextType) -> None:
        self.object = new_object

    def __str__(self):
        return self.plain_text

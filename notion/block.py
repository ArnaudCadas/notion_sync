from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict

from notion.objects import RichText


@dataclass
class Block:
    id: str


@dataclass
class ParagraphBlock(Block):
    text: List[RichText]

    @classmethod
    def from_dict(cls, block_dict: Dict) -> ParagraphBlock:
        block_id = block_dict["id"]
        block_text_list = block_dict["paragraph"]["text"]
        if block_text_list:
            block_text = [RichText.from_dict(object_dict=rich_text)
                          for rich_text in block_text_list]
        else:
            block_text = []
        return cls(id=block_id, text=block_text)

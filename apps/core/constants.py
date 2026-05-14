from enum import StrEnum


class SlideLayout(StrEnum):
    TITLE = "title"
    CONTENT = "content"
    TWO_COLUMN = "two_column"
    IMAGE_LEFT = "image_left"
    IMAGE_RIGHT = "image_right"
    BLANK = "blank"

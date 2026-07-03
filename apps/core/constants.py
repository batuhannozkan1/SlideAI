from enum import StrEnum


# Legacy enum — kept only so historical migrations that reference it stay importable.
# Superseded by SlideType; do not use in new code.
class SlideLayout(StrEnum):
    TITLE = "title"
    CONTENT = "content"
    TWO_COLUMN = "two_column"
    IMAGE_LEFT = "image_left"
    IMAGE_RIGHT = "image_right"
    BLANK = "blank"


class SlideType(StrEnum):
    COVER = "cover"      # opening / title slide
    SPLIT = "split"      # most common content slide (left text + right visual)
    CLOSING = "closing"  # closing / summary slide


# Right-panel visual element types (registry-style; rendered by a partial per type).
class VisualType(StrEnum):
    DASHBOARD = "dashboard"
    BAR_CHART = "bar_chart"
    CARD_LIST = "card_list"
    TIMELINE = "timeline"
    DONUT = "donut"
    COMPARISON = "comparison"
    ICON_GRID = "icon_grid"
    STATUS_CARD = "status_card"

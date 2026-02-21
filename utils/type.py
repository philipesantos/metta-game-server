from enum import Enum


class Type(Enum):
    CHARACTER = "Character"
    LOCATION = "Location"
    ITEM = "Item"
    CONTAINER = "Container"
    PICKUPABLE = "Pickupable"
    ROUTE = "Route"
    ROUTE_BLOCK = "RouteBlock"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Location-based classes and functions.

import json


class Map:
    def __init__(self, name, scale=1, offset=0):
        """Initializes a new Map object.

        Args:
            name (str): The name of the map.
            scale (int|float): Scale factor for map locations.
            offset (int): Offset for map locations.
        """
        self.name = name
        self.scale = scale
        self.offset = offset

    def location(self, x, y, **kwargs):
        """Creates a new map location on the map.

        Args:
            x (int|float): The x-coordinate of the location.
            y (int|float): The y-coordinate of the location.

        Returns:
            MapLocation: The new map location.
        """
        return MapLocation(self, x, y, **kwargs)

    def simple_location(self, name, x, y, location_id=None, **kwargs):
        """Creates a single section location on the map.  For simple items that are only one check in one spot.

        Args:
            name (str): The name of the location.
            x (int|float): The x-coordinate of the location.
            y (int|float): The y-coordinate of the location.
            location_id (int|list[int]): The Archieplago location ID(s) for the location.

        Returns:
            Location: The new map location.
        """
        return Location(name, map_locations=[self.location(x, y)], sections=[Section(name, location_id=location_id)],
                        **kwargs)


class MapLocation:
    def __init__(self, map, x, y, size=None, border_thickness=None, restrict_visibility_rules=None,
                 force_invisibility_rules=None):
        """Initializes a new map coordinate location object.

        Args:
            map (Map): The map the location is on.
            x (int|float): The x-coordinate of the location.
            y (int|float): The y-coordinate of the location.
            size (int): The size of the location, if overriding the map.
            border_thickness (int): The thickness of the border around the location, if overriding the map.
            restrict_visibility_rules (list): A list of visibility rules to restrict visibility to the location.
            force_invisibility_rules (list): A list of visibility rules to force invisibility to the location.
        """
        self.map = map
        self.x = x
        self.y = y
        self.size = size
        self.border_thickness = border_thickness
        self.restrict_visibility_rules = restrict_visibility_rules
        self.force_invisibility_rules = force_invisibility_rules

    def __json__(self):
        obj = {
            'map': self.map.name,
            'x': int(self.x * self.map.scale) + self.map.offset,
            'y': int(self.y * self.map.scale) + self.map.offset,
        }
        if self.size:
            obj['size'] = self.size
        if self.border_thickness:
            obj['border_thickness'] = self.border_thickness
        if self.restrict_visibility_rules:
            obj['restrict_visibility_rules'] = self.restrict_visibility_rules
        if self.force_invisibility_rules:
            obj['force_invisibility_rules'] = self.force_invisibility_rules

        return obj


class Area:
    def __init__(self, name, short_name=None, access_rules=None, visibility_rules=None, chest_unopened_img=None,
                 chest_opened_img=None, overlay_background=None, color=None, parent=None, children=None):
        """Initializes a new Area object.

        Args:
            name (str): The full name of the area.
            short_name (str): The short name of the area.
            access_rules (list): A list of access rules for the area.
            visibility_rules (list): A list of visibility rules for the area.
            chest_unopened_img (str): The image to use for unopened chests in the area.
            chest_opened_img (str): The image to use for opened chests in the area.
            overlay_background (str): Background colour for number of opened chests.
            color (str): The colour to use for the area tooltip.
            parent (str): Override area's parent to put it in a different location in the JSON output.
            children (list[Area|Location]): A list of child areas or locations for the area.  Areas can be nested.
        """
        self.name = name
        self.short_name = short_name
        self.access_rules = access_rules or []
        self.visibility_rules = visibility_rules
        self.chest_unopened_img = chest_unopened_img
        self.chest_opened_img = chest_opened_img
        self.overlay_background = overlay_background
        self.color = color
        self.parent = parent
        self.children = children or []

    def __json__(self):
        obj = {
            'name': self.name,
        }
        if self.short_name:
            obj['short_name'] = self.short_name
        if self.access_rules:
            obj['access_rules'] = self.access_rules
        if self.visibility_rules:
            obj['visibility_rules'] = self.visibility_rules
        if self.chest_unopened_img:
            obj['chest_unopened_img'] = self.chest_unopened_img
        if self.chest_opened_img:
            obj['chest_opened_img'] = self.chest_opened_img
        if self.overlay_background:
            obj['overlay_background'] = self.overlay_background
        if self.color:
            obj['color'] = self.color
        if self.parent:
            obj['parent'] = self.parent
        obj['children'] = self.children
        return obj


class Location:
    def __init__(self, name, access_rules=None, chest_unopened_img=None, chest_opened_img=None, map_locations=None,
                 sections=None):
        """Initializes a new Location object.

        Args:
            name (str): The name of the location.
            access_rules (list): A list of access rules for the location.
            chest_unopened_img (str): The image to use for unopened chests in the location.
            chest_opened_img (str): The image to use for opened chests in the location.
            map_locations (list[MapLocation]): A list of map locations for the location.
            sections (list[Section]): A list of sections for the location.
        """
        self.name = name
        self.access_rules = access_rules or []
        self.chest_unopened_img = chest_unopened_img
        self.chest_opened_img = chest_opened_img
        self.map_locations = map_locations or []
        self.sections = sections or []

    def __json__(self):
        obj = {
            'name': self.name,
        }
        if self.access_rules:
            obj['access_rules'] = self.access_rules
        if self.chest_unopened_img:
            obj['chest_unopened_img'] = self.chest_unopened_img
        if self.chest_opened_img:
            obj['chest_opened_img'] = self.chest_opened_img
        if self.sections:
            obj['sections'] = self.sections
        if self.map_locations:
            obj['map_locations'] = self.map_locations
        return obj


class Section:
    def __init__(self, name, clear_as_group=False, chest_unopened_img=None, chest_opened_img=None, item_count=None,
                 hosted_item=None, access_rules=None, visibility_rules=None, location_id=None):
        """Initializes a new Section object.

        Args:
            name (str): The name of the section.
            clear_as_group (bool): Whether the section is cleared as a group.
            chest_unopened_img (str): The image to use for unopened chests in the section.
            chest_opened_img (str): The image to use for opened chests in the section.
            item_count (int): The number of items in the section.
            hosted_item (str): This item will be checked when cleared.
            access_rules (list): A list of access rules for the section.
            visibility_rules (list): A list of visibility rules for the section.
            location_id (int|list[int]): The Archieplago location ID(s) for the location.
        """
        self.name = name
        self.clear_as_group = clear_as_group
        self.chest_unopened_img = chest_unopened_img
        self.chest_opened_img = chest_opened_img
        self.hosted_item = hosted_item
        self.access_rules = access_rules or []
        self.visibility_rules = visibility_rules

        # Reference to Archipelago location ID(s).  This isn't part of the JSON output, but we can track it internally.
        self.location_id = location_id

        # If we didn't pass item count, default to 1 OR number of AP location IDs.
        if item_count is None:
            if isinstance(self.location_id, (list, tuple)):
                item_count = len(self.location_id)
            else:
                item_count = 1

        self.item_count = item_count

    def __json__(self):
        obj = {
            'name': self.name,
        }
        # For hosted items with a count of 1 (e.g. boss kills), don't include the item count.
        if self.item_count != 1 or not self.hosted_item:
            obj['item_count'] = self.item_count
        if self.clear_as_group:
            obj['clear_as_group'] = self.clear_as_group
        if self.chest_unopened_img:
            obj['chest_unopened_img'] = self.chest_unopened_img
        if self.chest_opened_img:
            obj['chest_opened_img'] = self.chest_opened_img
        if self.access_rules:
            obj['access_rules'] = self.access_rules
        if self.visibility_rules:
            obj['visibility_rules'] = self.visibility_rules
        if self.hosted_item:
            obj['hosted_item'] = self.hosted_item
        return obj


def import_locations_from_file(file_path):
    """Imports locations from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        list[Location]: The imported locations.
    """

    locations = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Filter out comment lines (even though JSON doesn't technically support that).
    lines = [line for line in lines if not line.strip().startswith('//')]
    data = json.loads(''.join(lines))

    for d in data:
        locations.append(_handle_location_data(d))

    return locations


def _handle_location_data(data):
    """Handles location data recursively.

    Args:
        data (dict): The location data.

    Returns:
        Area|Location: The new area or location object.
    """

    # If we have children, this is an Area object.
    if 'children' in data:
        location = Area(data['name'])
        for c in data['children']:
            location.children.append(_handle_location_data(c))

    # Otherwise, it's a single location.
    else:
        location = Location(data['name'])

        if data.get('sections'):
            for s in data['sections']:
                location.sections.append(
                    Section(s['name'], clear_as_group=s.get('clear_as_group', False),
                            chest_unopened_img=s.get('chest_unopened_img'), chest_opened_img=s.get('chest_opened_img'),
                            item_count=s.get('item_count'), hosted_item=s.get('hosted_item'),
                            access_rules=s.get('access_rules'), visibility_rules=s.get('visibility_rules'),
                            location_id=s.get('location_id')))

        if data.get('map_locations'):
            for m in data['map_locations']:
                location.map_locations.append(
                    MapLocation(Map(m['map']), m['x'], m['y'], size=m.get('size'),
                                border_thickness=m.get('border_thickness'),
                                restrict_visibility_rules=m.get('restrict_visibility_rules'),
                                force_invisibility_rules=m.get('force_invisibility_rules')))

    if data.get('access_rules'):
        location.access_rules = data['access_rules']

    return location

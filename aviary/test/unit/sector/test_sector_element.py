
import pytest

import geojson


import aviary.sector.sector_element as se


def test_boundary_geojson(i_element):

    result = i_element.boundary_geojson()

    assert sorted(result.keys()) == [se.GEOMETRY_KEY, se.PROPERTIES_KEY, se.TYPE_KEY]
    assert result[se.GEOMETRY_KEY][se.TYPE_KEY] == 'Polygon'

    assert isinstance(result[se.PROPERTIES_KEY], dict)
    assert sorted(result[se.PROPERTIES_KEY].keys()) == \
           sorted([se.NAME_KEY, se.LOWER_LIMIT_KEY, se.ROUTES_KEY, se.TYPE_KEY, se.UPPER_LIMIT_KEY])

    assert isinstance(result[se.PROPERTIES_KEY][se.ROUTES_KEY], dict)
    assert sorted(result[se.PROPERTIES_KEY][se.ROUTES_KEY].keys()) == sorted(i_element.shape.route_names)

def test_waypoint_geojson(i_element):

    name = 'b'.upper()
    result = i_element.waypoint_geojson(name)

    assert sorted(result.keys()) == [se.GEOMETRY_KEY, se.PROPERTIES_KEY, se.TYPE_KEY]
    assert result[se.GEOMETRY_KEY][se.TYPE_KEY] == 'Point'
    assert result[se.PROPERTIES_KEY][se.NAME_KEY] == name.upper()
    assert result[se.PROPERTIES_KEY][se.TYPE_KEY] == se.FIX_VALUE

def test_route_geojson(i_element):

    route_index = 1
    result = i_element.route_geojson(route_index = route_index)

    assert sorted(result.keys()) == [se.GEOMETRY_KEY, se.PROPERTIES_KEY, se.TYPE_KEY]
    assert sorted(result[se.PROPERTIES_KEY]) == [se.LATITUDES_KEY, se.LONGITUDES_KEY, se.NAME_KEY, se.POINTS_KEY, se.TYPE_KEY]
    assert len(result[se.PROPERTIES_KEY][se.LATITUDES_KEY]) == 5
    assert len(result[se.PROPERTIES_KEY][se.LONGITUDES_KEY]) == 5
    assert result[se.PROPERTIES_KEY][se.NAME_KEY] == i_element.shape.route_names[route_index]
    assert len(result[se.PROPERTIES_KEY][se.POINTS_KEY]) == 5
    assert result[se.PROPERTIES_KEY][se.TYPE_KEY] == se.ROUTE_VALUE

    assert isinstance(result[se.GEOMETRY_KEY], dict)
    assert sorted(result[se.GEOMETRY_KEY].keys()) == ['coordinates', se.TYPE_KEY]

    assert isinstance(result[se.GEOMETRY_KEY]['coordinates'], list)
    assert len(result[se.GEOMETRY_KEY]['coordinates']) == len(result[se.PROPERTIES_KEY][se.POINTS_KEY])


def test_geo_interface(y_element):

    result = y_element.__geo_interface__

    assert sorted(result.keys()) == [se.FEATURES_KEY]

    # The result contains one feature per route and per waypoint, plus one for the boundary.
    assert len(result[se.FEATURES_KEY]) == len(y_element.shape.route_names) + len(y_element.shape.fixes) + 1


def test_serialisation(x_element):
    # Test JSON serialisation/deserialisation.

    serialised = geojson.dumps(x_element, sort_keys=True, indent = 4)

    deserialised = geojson.loads(serialised)

    assert isinstance(deserialised, dict)
    assert list(deserialised.keys()) == [se.FEATURES_KEY]


# def test_write_geojson(x_element):
#     # Test JSON serialisation/deserialisation.
#
#     x_element.write_geojson(filename = "x_sector_hell")

"""
Represents a route through a sector shape or element.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

from shapely.geometry import LineString, mapping

import aviary.sector.sector_element as se
from aviary.geo.geo_helper import GeoHelper

FIX_NAME_KEY = "fixName"

class Route():
    """A route through a sector.

    Each route is a list of fixes, and each fix is a (string, Point) pair
    where the string is the name of the fix and the Point is its x-y coordinate.

    Optionally a projection function may be included, in which case the instance
    represents a route through a (projected) sector element. If the projection
    attribute is None, the route is through a (flat, 2D) sector shape.

    """

    def __init__(self, name, fix_list, projection = None):
        """
        Route class constructor.

        :param name: The name of the route
        :param fix_list: A list of (str, shapely.point.Point) pairs
        :param projection: (optional) a pyproj Projection object
        """

        self.name = name
        self.fix_list = fix_list
        self.projection = projection


    def copy(self):
        """Returns a deep copy of a Route instance"""

        return Route(self.name, fix_list = self.fix_list.copy(), projection = self.projection)


    def reverse(self):
        """Reverses the Route instance"""

        self.name = self.name[::-1]
        self.fix_list = self.fix_list[::-1]


    def length(self):
        """Returns the number of fixes in the route"""

        return len(self.fix_list)


    def fix_names(self):
        """Returns the names of the fixes in the route"""

        return [i[0] for i in self.fix_list]


    def fix_points(self, unprojected = False):
        """Returns the coordinates of the fixes in the route"""

        # Project the coordinates unless the projection attribute is not None or unprojected is True.
        if unprojected or self.projection is None:
            return [i[1] for i in self.fix_list]

        return [GeoHelper.__inv_project__(self.projection, geom=i[1]) for i in self.fix_list]


    @property
    def __geo_interface__(self) -> dict:
        """
        Implements the geo interface (see https://gist.github.com/sgillies/2217756#__geo_interface__)
        Returns a GeoJSON dictionary. For serialisation and deserialisation, use geojson.dumps and geojson.loads.
        """
        return self.geojson()


    def geojson(self) -> dict:
        """
        Returns a GeoJSON dictionary representing the route

        A route includes elements:
        - type: "Feature"
        - geometry: a LineString feature whose properties are a list of points, with long/lat coordinates
        - properties:
           - name: e.g. "DAMNATION"
           - type: "ROUTE"
           - children: {"FIX": {"names": [<route fix names>]}}
        """

        geojson = {
            se.TYPE_KEY: se.FEATURE_VALUE,
            se.PROPERTIES_KEY: {
                se.NAME_KEY: self.name,
                se.TYPE_KEY: se.ROUTE_VALUE,
                se.CHILDREN_KEY: {
                    se.FIX_VALUE: {
                        se.CHILDREN_NAMES_KEY: self.fix_names()
                    }
                }
            },
            se.GEOMETRY_KEY: GeoHelper.__inv_project__(self.projection,
                geom = LineString(self.fix_points(unprojected = True))).__geo_interface__
        }

        # Fix issue with __geo_interface__ unexpectedly returning a tuple of coordinates rather than a list.
        geojson = GeoHelper.fix_geometry_coordinates_tuple(geojson, key = se.GEOMETRY_KEY)
        return geojson


    def serialize(self):
        """Serialises the route instance as a JSON string"""

        return [
            {
                FIX_NAME_KEY: self.fix_names()[i],
                se.GEOMETRY_KEY: self.fix_points()[i].__geo_interface__
            }
            for i in range(self.length())
        ]


    def truncate(self, initial_lat, initial_lon):
        """Truncates this route in light of a given start position by removing fixes that are already passed."""

        if not self.projection:
            raise ValueError("Truncate route operation requires a non-empty projection attribute.")

        # Retain only those route elements that are closer to the final fix than the start_position.
        final_lon, final_lat = self.fix_points()[-1].coords[0]  # Note lon/lat order!
        self.fix_list = [self.fix_list[i] for i in range(self.length()) if
                         GeoHelper.distance(lat1 = final_lat, lon1 = final_lon, lat2 = self.fix_points()[i].coords[0][1], lon2 = self.fix_points()[i].coords[0][0]) <
                         GeoHelper.distance(lat1 = final_lat, lon1 = final_lon, lat2 = initial_lat, lon2 = initial_lon)]

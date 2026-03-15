import unittest

from core.patterns.facts.route_description_fact_pattern import (
    RouteDescriptionFactPattern,
)
from utils.type import Type


class TestRouteDescriptionFactPattern(unittest.TestCase):
    def test_to_metta(self):
        location_from = "glade"
        direction = "south"
        location_to = "cave"
        description = "A narrow trail descends into shadow."
        route_description = RouteDescriptionFactPattern(
            location_from,
            direction,
            location_to,
            description,
        )
        self.assertEqual(
            route_description.to_metta(),
            f'({Type.ROUTE_DESCRIPTION.value} {location_from} {direction} '
            f'{location_to} "{description}")',
        )


if __name__ == "__main__":
    unittest.main()

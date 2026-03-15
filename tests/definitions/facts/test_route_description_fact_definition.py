import unittest

from core.definitions.facts.route_description_fact_definition import (
    RouteDescriptionFactDefinition,
)
from core.patterns.facts.route_description_fact_pattern import (
    RouteDescriptionFactPattern,
)
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.direction import Direction


class TestRouteDescriptionFactDefinition(unittest.TestCase):
    def test_to_metta(self):
        metta = get_test_metta()

        location_from = "glade"
        direction = Direction.SOUTH.value
        location_to = "cave"
        description = "A narrow trail descends into shadow."

        metta.run(
            RouteDescriptionFactDefinition(
                location_from,
                direction,
                location_to,
                description,
            ).to_metta()
        )

        route_description_from = RouteDescriptionFactPattern(
            "$from",
            direction,
            location_to,
            description,
        )
        result_from = metta.run(
            f"!(match &self {route_description_from.to_metta()} $from)"
        )
        self.assertEqual(unwrap_first_match(result_from), location_from)

        route_description_direction = RouteDescriptionFactPattern(
            location_from,
            "$direction",
            location_to,
            description,
        )
        result_direction = metta.run(
            f"!(match &self {route_description_direction.to_metta()} $direction)"
        )
        self.assertEqual(unwrap_first_match(result_direction), direction)

        route_description_to = RouteDescriptionFactPattern(
            location_from,
            direction,
            "$to",
            description,
        )
        result_to = metta.run(f"!(match &self {route_description_to.to_metta()} $to)")
        self.assertEqual(unwrap_first_match(result_to), location_to)

        route_description_text = RouteDescriptionFactPattern(
            location_from,
            direction,
            location_to,
            "$description",
        )
        result_text = metta.run(
            f"!(match &self {route_description_text.to_metta()} $description)"
        )
        self.assertEqual(unwrap_first_match(result_text), description)


if __name__ == "__main__":
    unittest.main()

import unittest

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.patterns.facts.container_fact_pattern import ContainerFactPattern
from core.patterns.facts.location_fact_pattern import LocationFactPattern
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.type import Type


class TestContainerFactDefinition(unittest.TestCase):
    def test_to_metta(self):
        metta = get_test_metta()

        key = "chest"
        metta.run(ContainerFactDefinition(key).to_metta())

        result_type = metta.run(f"!(get-type {key})")
        self.assertEqual(unwrap_first_match(result_type), Type.CONTAINER.value)

        container_key = ContainerFactPattern("$key")
        result_key = metta.run(f"!(match &self {container_key.to_metta()} $key)")
        self.assertEqual(unwrap_first_match(result_key), key)

        no_match = LocationFactPattern("bottle")
        result_no_match = metta.run(f"!(match &self {no_match.to_metta()} True)")
        self.assertEqual(result_no_match, [[]])


if __name__ == "__main__":
    unittest.main()

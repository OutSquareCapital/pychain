import unittest
from dataclasses import dataclass
from typing import Any

import pychain as pc


@dataclass(slots=True)
class TestData:
    values: list[int]
    names: list[str]
    active: list[bool]


@dataclass(slots=True)
class ResultData(TestData):
    filtered_values: list[int]
    names_with_a: list[str]
    reversed_values: list[int]
    sliced_values: list[int]


class TestIterExprIntegration(unittest.TestCase):
    """Tests for integration between Iter and Expr classes."""

    def test_record_with_expr_transformations(self):
        """Test using Expr to transform data in a Record."""
        # Create test data
        data = pc.Dict[str, Any](
            {
                "values": [1, 2, 3, 4, 5],
                "names": ["Alice", "Bob", "Charlie", "Dave", "Eva"],
                "active": [True, False, True, True, False],
            }
        )

        # Use with_fields with expressions that use BaseProcess/BaseFilter methods
        result = ResultData(
            **data.with_fields(
                pc.key("values")
                .filter(lambda x: x > 2)
                .apply(list)
                .alias("filtered_values"),
                pc.key("names")
                .filter_contain("a", str.lower)
                .apply(list)
                .alias("names_with_a"),
                pc.key("values").reverse().apply(list).alias("reversed_values"),
                pc.key("values").slice(1, 4).apply(list).alias("sliced_values"),
            ).unwrap()
        )

        # Verify results
        self.assertEqual(result.filtered_values, [3, 4, 5])
        self.assertEqual(result.names_with_a, ["Alice", "Charlie", "Dave", "Eva"])
        self.assertEqual(result.reversed_values, [5, 4, 3, 2, 1])
        self.assertEqual(result.sliced_values, [2, 3, 4])

        # Original fields should still be present
        self.assertEqual(result.values, [1, 2, 3, 4, 5])
        self.assertEqual(result.names, ["Alice", "Bob", "Charlie", "Dave", "Eva"])
        self.assertEqual(result.active, [True, False, True, True, False])

    def test_iter_and_expr_comparable_results(self):
        """Test that Iter and Expr produce the same results for complex operations."""
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        # Using Iter
        iter_result = (
            pc.Iter(test_data)
            .filter(lambda x: x % 2 == 0)  # Even numbers
            .map(lambda x: x * 2)  # Double them
            .accumulate(lambda a, b: a + b)  # Running sum
            .into(list)
        )

        # Using Expr in a Record
        record = pc.Dict({"numbers": test_data})

        expr_result = (
            record.with_fields(
                pc.key("numbers")
                .filter(lambda x: x % 2 == 0)  # Even numbers
                .map(lambda x: x * 2)  # Double them
                .accumulate(lambda a, b: a + b)  # Running sum
                .apply(list)
                .alias("result")
            )
            .unwrap()
            .get("result")
        )

        # Both should produce the same result
        self.assertEqual(iter_result, expr_result)

    def test_processing_nested_data(self):
        """Test processing nested data with both Iter and Expr."""
        data = {
            "users": [
                {"name": "Alice", "scores": [85, 90, 78]},
                {"name": "Bob", "scores": [92, 88, 95]},
                {"name": "Charlie", "scores": [75, 80, 65]},
            ]
        }

        iter_result = (
            pc.Iter(data["users"])
            .filter(lambda user: sum(user["scores"]) / len(user["scores"]) >= 85)  # type: ignore
            .pluck("name")
            .into(list)
        )
        # Using Expr with the same logic
        expr_result = (
            pc.Dict(data)
            .with_fields(
                pc.key("users")
                .filter(lambda user: sum(user["scores"]) / len(user["scores"]) >= 85)
                .pluck("name")
                .apply(list)
                .alias("high_scorers")
            )
            .unwrap()
            .get("high_scorers")
        )

        self.assertEqual(iter_result, expr_result)
        expected_result = [
            user["name"]
            for user in data["users"]
            if sum(user["scores"]) / len(user["scores"]) >= 85  # type: ignore
        ]
        self.assertEqual(iter_result, expected_result)


if __name__ == "__main__":
    unittest.main()

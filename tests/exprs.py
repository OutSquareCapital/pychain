import unittest
from dataclasses import dataclass
from typing import Any, TypedDict

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


class UserScores(TypedDict):
    name: str
    scores: list[int]


class UsersData(TypedDict):
    users: list[UserScores]


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
                .itr(lambda x: x.filter(lambda x: x > 2).into(list))
                .alias("filtered_values"),
                pc.key("names")
                .itr(lambda x: x.filter_contain("a", str.lower).into(list))
                .alias("names_with_a"),
                pc.key("values")
                .itr(lambda x: x.reverse().into(list))
                .alias("reversed_values"),
                pc.key("values")
                .itr(lambda x: x.slice(1, 4).into(list))
                .alias("sliced_values"),
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
                .itr(
                    lambda x: x.filter(lambda x: x % 2 == 0)  # Even numbers
                    .map(lambda x: x * 2)  # Double them
                    .accumulate(lambda a, b: a + b)  # Running sum
                    .into(list)
                )
                .alias("result")
            )
            .unwrap()
            .get("result")
        )

        # Both should produce the same result
        self.assertEqual(iter_result, expr_result)

    def test_processing_nested_data(self):
        """Test processing nested data with both Iter and Expr."""
        data = UsersData(
            {
                "users": [
                    {"name": "Alice", "scores": [85, 90, 78]},
                    {"name": "Bob", "scores": [92, 88, 95]},
                    {"name": "Charlie", "scores": [75, 80, 65]},
                ]
            }
        )

        def _high_scorers(user: UserScores) -> bool:
            return sum(user["scores"]) / len(user["scores"]) >= 85

        iter_result: list[str] = (
            pc.Iter(data["users"])
            .filter(_high_scorers)
            .map(lambda x: x["name"])
            .into(list)
        )
        expr_itr_result = (
            pc.Dict(data)
            .select(
                pc.key("users").itr(
                    lambda users: users.filter(_high_scorers)
                    .map(lambda x: x["name"])
                    .into(list)
                )
            )
            .unwrap()
            .get("users")
        )
        expected_result: list[str] = [
            user["name"] for user in data["users"] if _high_scorers(user)
        ]
        self.assertEqual(iter_result, expr_itr_result)
        self.assertEqual(iter_result, expected_result)


if __name__ == "__main__":
    unittest.main()

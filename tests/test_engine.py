"""Tests for the calculator backend engine."""

import pytest

from backend import EvaluationError, evaluate_expression


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("1+2", 3),
        ("4-2", 2),
        ("3*5", 15),
        ("8/2", 4),
        ("1.5+2.5", 4.0),
    ],
)
def test_arithmetic(expression: str, expected: float) -> None:
    assert evaluate_expression(expression) == expected


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("(2+3)*4", 20),
        ("-3 + 5", 2),
        ("+6", 6),
    ],
)
def test_parentheses_and_unary(expression: str, expected: float) -> None:
    assert evaluate_expression(expression) == expected


@pytest.mark.parametrize(
    "expression, match",
    [
        ("", "Enter an expression"),
        ("2**3", "Unsupported|Invalid"),
    ],
)
def test_invalid_expression(expression: str, match: str) -> None:
    with pytest.raises(EvaluationError, match=match):
        evaluate_expression(expression)


def test_divide_by_zero() -> None:
    with pytest.raises(EvaluationError, match="(?i)divide by zero"):
        evaluate_expression("1/0")

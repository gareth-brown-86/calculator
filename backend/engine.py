"""Safe expression evaluation for basic arithmetic."""

from __future__ import annotations

import ast
from typing import Union

Number = Union[int, float]


class EvaluationError(Exception):
    """Raised when expression evaluation fails."""


def evaluate_expression(expression: str) -> Number:
    """Evaluate a basic arithmetic expression safely.

    Supports +, -, *, /, parentheses, and unary +/-. Raises EvaluationError for
    invalid input.
    """
    cleaned = (expression or "").strip()
    if not cleaned:
        raise EvaluationError("Enter an expression to calculate.")

    try:
        parsed = ast.parse(cleaned, mode="eval")
    except SyntaxError as exc:
        raise EvaluationError("Invalid expression.") from exc

    result = _eval_node(parsed.body)
    if isinstance(result, bool):
        raise EvaluationError("Invalid expression.")
    return result


def _eval_node(node: ast.AST) -> Number:
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _apply_operator(node.op, left, right)
    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        return _apply_unary(node.op, operand)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise EvaluationError("Only numbers are allowed.")
    raise EvaluationError("Invalid expression.")


def _apply_operator(op: ast.operator, left: Number, right: Number) -> Number:
    if isinstance(op, ast.Add):
        return left + right
    if isinstance(op, ast.Sub):
        return left - right
    if isinstance(op, ast.Mult):
        return left * right
    if isinstance(op, ast.Div):
        if right == 0:
            raise EvaluationError("Cannot divide by zero.")
        return left / right
    raise EvaluationError("Unsupported operator.")


def _apply_unary(op: ast.unaryop, value: Number) -> Number:
    if isinstance(op, ast.UAdd):
        return +value
    if isinstance(op, ast.USub):
        return -value
    raise EvaluationError("Unsupported unary operator.")

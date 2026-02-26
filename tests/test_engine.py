from backend import EvaluationError, evaluate_expression


def test_basic_operations():
    assert evaluate_expression("1+2") == 3
    assert evaluate_expression("4-2") == 2
    assert evaluate_expression("3*5") == 15
    assert evaluate_expression("8/2") == 4


def test_parentheses_and_unary():
    assert evaluate_expression("(2+3)*4") == 20
    assert evaluate_expression("-3 + 5") == 2
    assert evaluate_expression("+6") == 6


def test_decimal_support():
    assert evaluate_expression("1.5+2.5") == 4.0


def test_invalid_expression():
    try:
        evaluate_expression("")
        assert False, "Expected EvaluationError"
    except EvaluationError as exc:
        assert "Enter an expression" in str(exc)

    try:
        evaluate_expression("2**3")
        assert False, "Expected EvaluationError"
    except EvaluationError as exc:
        assert "Unsupported" in str(exc) or "Invalid" in str(exc)


def test_divide_by_zero():
    try:
        evaluate_expression("1/0")
        assert False, "Expected EvaluationError"
    except EvaluationError as exc:
        assert "divide by zero" in str(exc).lower()

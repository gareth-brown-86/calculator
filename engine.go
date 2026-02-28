// Package main provides a safe arithmetic expression evaluator.
//
// Supported: +, -, *, /, parentheses, unary +/-, integers and floats.
// Forbidden: everything else (no variables, function calls, or exponentiation).
package main

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
	"unicode"
)

// EvaluationError is returned when the expression cannot be evaluated.
type EvaluationError struct {
	Message string
}

func (e *EvaluationError) Error() string { return e.Message }

// Evaluate parses and evaluates a basic arithmetic expression.
func Evaluate(expr string) (float64, error) {
	expr = strings.TrimSpace(expr)
	if expr == "" {
		return 0, &EvaluationError{"Enter an expression to calculate."}
	}

	p := &parser{input: expr}
	result, err := p.parseExpression()
	if err != nil {
		return 0, err
	}
	p.skipSpaces()
	if p.pos < len(p.input) {
		return 0, &EvaluationError{"Invalid expression."}
	}
	return result, nil
}

// FormatResult renders a float64 nicely: drop ".0" for integers.
func FormatResult(v float64) string {
	if v == float64(int64(v)) && v >= -1e15 && v <= 1e15 {
		return strconv.FormatInt(int64(v), 10)
	}
	s := fmt.Sprintf("%.10g", v)
	return s
}

// ── Recursive-descent parser ────────────────────────────────────────────────

type parser struct {
	input string
	pos   int
}

func (p *parser) peek() byte {
	p.skipSpaces()
	if p.pos >= len(p.input) {
		return 0
	}
	return p.input[p.pos]
}

func (p *parser) skipSpaces() {
	for p.pos < len(p.input) && p.input[p.pos] == ' ' {
		p.pos++
	}
}

// parseExpression handles + and - (lowest precedence).
func (p *parser) parseExpression() (float64, error) {
	left, err := p.parseTerm()
	if err != nil {
		return 0, err
	}
	for {
		op := p.peek()
		if op != '+' && op != '-' {
			break
		}
		p.pos++ // consume operator
		right, err := p.parseTerm()
		if err != nil {
			return 0, err
		}
		if op == '+' {
			left += right
		} else {
			left -= right
		}
	}
	return left, nil
}

// parseTerm handles * and / (higher precedence).
func (p *parser) parseTerm() (float64, error) {
	left, err := p.parseUnary()
	if err != nil {
		return 0, err
	}
	for {
		op := p.peek()
		if op != '*' && op != '/' {
			break
		}
		p.pos++ // consume operator
		right, err := p.parseUnary()
		if err != nil {
			return 0, err
		}
		if op == '*' {
			left *= right
		} else {
			if right == 0 {
				return 0, &EvaluationError{"Cannot divide by zero."}
			}
			left /= right
		}
	}
	return left, nil
}

// parseUnary handles unary + and -.
func (p *parser) parseUnary() (float64, error) {
	ch := p.peek()
	if ch == '+' {
		p.pos++
		return p.parseUnary()
	}
	if ch == '-' {
		p.pos++
		val, err := p.parseUnary()
		if err != nil {
			return 0, err
		}
		return -val, nil
	}
	return p.parsePrimary()
}

// parsePrimary handles numbers and parenthesised sub-expressions.
func (p *parser) parsePrimary() (float64, error) {
	ch := p.peek()

	// Parenthesised expression
	if ch == '(' {
		p.pos++
		val, err := p.parseExpression()
		if err != nil {
			return 0, err
		}
		if p.peek() != ')' {
			return 0, &EvaluationError{"Missing closing parenthesis."}
		}
		p.pos++
		return val, nil
	}

	// Number
	return p.parseNumber()
}

func (p *parser) parseNumber() (float64, error) {
	p.skipSpaces()
	start := p.pos
	for p.pos < len(p.input) && (unicode.IsDigit(rune(p.input[p.pos])) || p.input[p.pos] == '.') {
		p.pos++
	}
	// Reject ** (exponentiation) or any letter immediately after number
	if p.pos < len(p.input) {
		next := p.input[p.pos]
		if unicode.IsLetter(rune(next)) {
			return 0, &EvaluationError{"Invalid expression."}
		}
	}
	if start == p.pos {
		return 0, &EvaluationError{"Invalid expression."}
	}
	val, err := strconv.ParseFloat(p.input[start:p.pos], 64)
	if err != nil {
		return 0, &EvaluationError{"Invalid number."}
	}
	return val, nil
}

// IsEvaluationError checks whether an error is an EvaluationError.
func IsEvaluationError(err error) bool {
	var evalErr *EvaluationError
	return errors.As(err, &evalErr)
}

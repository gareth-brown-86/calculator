package main

import (
	"testing"
)

func TestArithmetic(t *testing.T) {
	tests := []struct {
		expr string
		want float64
	}{
		{"1+2", 3},
		{"4-2", 2},
		{"3*5", 15},
		{"8/2", 4},
		{"1.5+2.5", 4.0},
		{"10 + 20", 30},
		{"100 / 4 / 5", 5},
	}
	for _, tc := range tests {
		t.Run(tc.expr, func(t *testing.T) {
			got, err := Evaluate(tc.expr)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.want {
				t.Errorf("Evaluate(%q) = %v, want %v", tc.expr, got, tc.want)
			}
		})
	}
}

func TestParenthesesAndUnary(t *testing.T) {
	tests := []struct {
		expr string
		want float64
	}{
		{"(2+3)*4", 20},
		{"-3 + 5", 2},
		{"+6", 6},
		{"-(4+1)", -5},
		{"(-3)*(-2)", 6},
	}
	for _, tc := range tests {
		t.Run(tc.expr, func(t *testing.T) {
			got, err := Evaluate(tc.expr)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.want {
				t.Errorf("Evaluate(%q) = %v, want %v", tc.expr, got, tc.want)
			}
		})
	}
}

func TestInvalidExpressions(t *testing.T) {
	invalid := []string{
		"",
		"2**3",
		"abc",
		"2 + ",
		"hello + world",
	}
	for _, expr := range invalid {
		t.Run(expr, func(t *testing.T) {
			_, err := Evaluate(expr)
			if err == nil {
				t.Fatalf("expected error for %q, got nil", expr)
			}
			if !IsEvaluationError(err) {
				t.Errorf("expected EvaluationError for %q, got %T: %v", expr, err, err)
			}
		})
	}
}

func TestDivideByZero(t *testing.T) {
	_, err := Evaluate("1/0")
	if err == nil {
		t.Fatal("expected divide-by-zero error")
	}
	evalErr, ok := err.(*EvaluationError)
	if !ok {
		t.Fatalf("expected *EvaluationError, got %T", err)
	}
	if evalErr.Message != "Cannot divide by zero." {
		t.Errorf("unexpected message: %s", evalErr.Message)
	}
}

func TestFormatResult(t *testing.T) {
	tests := []struct {
		val  float64
		want string
	}{
		{3, "3"},
		{4.5, "4.5"},
		{0, "0"},
		{-7, "-7"},
		{1.0 / 3.0, "0.3333333333"},
	}
	for _, tc := range tests {
		t.Run(tc.want, func(t *testing.T) {
			got := FormatResult(tc.val)
			if got != tc.want {
				t.Errorf("FormatResult(%v) = %q, want %q", tc.val, got, tc.want)
			}
		})
	}
}

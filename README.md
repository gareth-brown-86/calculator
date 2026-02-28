# Calculator

A calculator with a Go backend and vanilla HTML/CSS/JS frontend.
The Go server evaluates arithmetic expressions safely and serves the static UI.

## Prerequisites

- [Go](https://go.dev/dl/) 1.21+

## Run

```bash
go run .
```

Open http://localhost:8080. Set `PORT` to change the port:

```bash
PORT=3000 go run .
```

## Build

```bash
go build -o calculator .
./calculator
```

## Tests

```bash
go test -v
```

## Features

- Click keypad buttons **or** type on your keyboard — focus stays on the input
- Supports `+`, `-`, `*`, `/`, parentheses, unary operators
- Calculation history with one-click reload
- Catppuccin Mocha dark theme
- Single binary — frontend is embedded at compile time

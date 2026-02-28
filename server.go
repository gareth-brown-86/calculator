// Package main – Calculator HTTP server.
//
// Serves the static frontend (static/) and exposes POST /api/evaluate.
package main

import (
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"log"
	"net/http"
	"os"
)

//go:embed static/*
var staticFiles embed.FS

type evalRequest struct {
	Expression string `json:"expression"`
}

type evalResponse struct {
	Result string `json:"result,omitempty"`
	Error  string `json:"error,omitempty"`
}

func handleEvaluate(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req evalRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(evalResponse{Error: "Invalid JSON body."})
		return
	}

	result, err := Evaluate(req.Expression)

	w.Header().Set("Content-Type", "application/json")

	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(evalResponse{Error: err.Error()})
		return
	}

	json.NewEncoder(w).Encode(evalResponse{Result: FormatResult(result)})
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Serve static files from the embedded filesystem.
	staticFS, err := fs.Sub(staticFiles, "static")
	if err != nil {
		log.Fatal(err)
	}
	http.Handle("/", http.FileServer(http.FS(staticFS)))
	http.HandleFunc("/api/evaluate", handleEvaluate)

	addr := fmt.Sprintf(":%s", port)
	log.Printf("Calculator running on http://localhost%s", addr)
	log.Fatal(http.ListenAndServe(addr, nil))
}

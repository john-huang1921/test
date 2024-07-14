package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

type Message struct {
	Username string `json:"username"`
	Content  string `json:"content"`
}

var chatHistory []Message

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println(err)
		return
	}
	defer conn.Close()

	for {
		var msg Message
		err := conn.ReadJSON(&msg)
		if err != nil {
			log.Println(err)
			break
		}
		chatHistory = append(chatHistory, msg)
		err = conn.WriteJSON(msg)
		if err != nil {
			log.Println(err)
			break
		}
	}
}

func downloadHandler(w http.ResponseWriter, r *http.Request) {
	data, err := json.Marshal(chatHistory)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Disposition", "attachment; filename=chat_history.json")
	w.Header().Set("Content-Type", "application/json")
	w.Write(data)
}

func main() {
	http.HandleFunc("/ws", handleWebSocket)
	http.HandleFunc("/download", downloadHandler)
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "index.html")
	})

	fmt.Println("Server is running on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
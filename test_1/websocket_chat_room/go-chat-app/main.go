package main

import (
    "fmt"
    "log"
    "net/http"
    "io/ioutil"
    "github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool {
        return true
    },
}

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        log.Println(err)
        return
    }
    defer conn.Close()

    pythonWs, _, err := websocket.DefaultDialer.Dial("ws://localhost:8765", nil)
    if err != nil {
        log.Println(err)
        return
    }
    defer pythonWs.Close()

    go func() {
        for {
            _, message, err := pythonWs.ReadMessage()
            if err != nil {
                log.Println("讀取 Python 伺服器消息錯誤:", err)
                return
            }
            conn.WriteMessage(websocket.TextMessage, message)
        }
    }()

    for {
        _, message, err := conn.ReadMessage()
        if err != nil {
            log.Println("讀取客戶端消息錯誤:", err)
            return
        }
        pythonWs.WriteMessage(websocket.TextMessage, message)
    }
}

func clearHistory(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "只允許 POST 請求", http.StatusMethodNotAllowed)
        return
    }

    pythonWs, _, err := websocket.DefaultDialer.Dial("ws://localhost:8765", nil)
    if err != nil {
        log.Println(err)
        http.Error(w, "無法連接到聊天伺服器", http.StatusInternalServerError)
        return
    }
    defer pythonWs.Close()

    clearMsg := []byte(`{"type": "clear_history"}`)
    err = pythonWs.WriteMessage(websocket.TextMessage, clearMsg)
    if err != nil {
        log.Println(err)
        http.Error(w, "發送清除請求失敗", http.StatusInternalServerError)
        return
    }

    w.WriteHeader(http.StatusOK)
    fmt.Fprint(w, "聊天記錄已清除")
}

func downloadHistory(w http.ResponseWriter, r *http.Request) {
    content, err := ioutil.ReadFile("chat_history.json")
    if err != nil {
        log.Println(err)
        http.Error(w, "無法讀取聊天記錄", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Disposition", "attachment; filename=chat_history.json")
    w.Header().Set("Content-Type", "application/json")
    w.Write(content)
}


func getHistory(w http.ResponseWriter, r *http.Request) {
    content, err := ioutil.ReadFile("chat_history.json")
    if err != nil {
        log.Println(err)
        http.Error(w, "無法讀取聊天記錄", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    w.Write(content)
}

func main() {
    http.HandleFunc("/ws", handleWebSocket)
    http.HandleFunc("/clear", clearHistory)
    http.HandleFunc("/download", downloadHistory)
    http.HandleFunc("/history", getHistory)  // 新增此行
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        http.ServeFile(w, r, "index.html")
    })

    fmt.Println("Server is running on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
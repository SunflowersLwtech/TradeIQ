"use client";

type MessageHandler = (data: WebSocketMessage) => void;
type StatusHandler = (status: ConnectionStatus) => void;

export type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

export interface WebSocketMessage {
  type: string;
  content?: string;
  data?: Record<string, unknown>;
  timestamp?: string;
}

export class TradeIQWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private messageHandlers: Set<MessageHandler> = new Set();
  private statusHandlers: Set<StatusHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private status: ConnectionStatus = "disconnected";

  constructor(path: string = "/chat/", userId?: string) {
    const wsBase = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
    const query = userId ? `?user_id=${encodeURIComponent(userId)}` : "";
    this.url = `${wsBase}${path}${query}`;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    this.setStatus("connecting");

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.setStatus("connected");
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WebSocketMessage;
          this.messageHandlers.forEach((handler) => handler(data));
        } catch {
          console.error("Failed to parse WebSocket message");
        }
      };

      this.ws.onclose = () => {
        this.setStatus("disconnected");
        this.attemptReconnect();
      };

      this.ws.onerror = () => {
        this.setStatus("error");
      };
    } catch {
      this.setStatus("error");
      this.attemptReconnect();
    }
  }

  disconnect(): void {
    this.reconnectAttempts = this.maxReconnectAttempts;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.setStatus("disconnected");
  }

  send(message: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  sendMessage(content: string): void {
    this.send({ type: "chat.message", message: content });
  }

  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  onStatusChange(handler: StatusHandler): () => void {
    this.statusHandlers.add(handler);
    return () => this.statusHandlers.delete(handler);
  }

  getStatus(): ConnectionStatus {
    return this.status;
  }

  private setStatus(status: ConnectionStatus): void {
    this.status = status;
    this.statusHandlers.forEach((handler) => handler(status));
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    setTimeout(() => {
      this.connect();
    }, delay);
  }
}

import logger from "../logger";
import urlResolver from "../urlResolver";
import { KERNEL_URL_CONFIG_PATH, KERNEL_BASE_URL } from "../constants";

export class SocketRequest {
  private _resolver: Promise<string>;

  constructor() {
    this._resolver = urlResolver(KERNEL_URL_CONFIG_PATH, KERNEL_BASE_URL);
  }

  async initialize(sendData: any) {
    const url = await this._resolver;
    const ws = new WebSocket(url);

    ws.onopen = (ev) => {
      this.onOpen(ev);
      ws.send(sendData);
    };
    ws.onclose = this.onClose;
    ws.onerror = this.onError;
    ws.onmessage = this.onMessage;
  }

  onOpen(_ev: Event) {
    logger.log("websocket: open");
  }
  onClose(_ev: Event) {
    logger.log("websocket: close");
  }
  onError(_ev: Event) {
    logger.error("websocket: error", _ev);
  }

  onMessage(ev: MessageEvent<string>) {
    logger.log("websocket: message", JSON.parse(ev.data));
  }

  sendMessage(message: any) {
    this.initialize(message);
  }
}

/**
 * Socket controller which keeps only one socket connection, not supported by kernel yet
 */
export class FutureSocketRequest {
  private _resolver: Promise<string>;
  private _ws?: WebSocket;

  constructor() {
    this._resolver = urlResolver(KERNEL_URL_CONFIG_PATH, KERNEL_BASE_URL);
    this.initialize();
  }

  async initialize() {
    if (this._ws) {
      this._ws.close();
    }

    const url = await this._resolver;
    this._ws = new WebSocket(url);

    this._ws.onopen = this.onOpen;
    this._ws.onclose = this.onClose;
    this._ws.onerror = this.onError;
    this._ws.onmessage = this.onMessage;
  }

  onOpen() {
    logger.log("websocket: open", this._ws?.url);
  }
  onClose() {
    logger.log("websocket: close");

    // keep this connection alive until app is done
    this.initialize();
  }
  onError(ev: Event) {
    logger.error("websocket: error", ev);
  }

  onMessage(ev: MessageEvent<string>) {
    logger.log("websocket: message", JSON.parse(ev.data));
  }

  send(data: any) {}
}

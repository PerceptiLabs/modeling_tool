export default class Worker {
  constructor(stringUrl) {
    this.url = stringUrl;
    this.onMessage = () => {};
    this.onEvent = () => {};
  }

  postMessage(msg) {
    this.onMessage(msg);
  }

  addEventListener(ev, el, option) {
    this.onEvent();
  }
}
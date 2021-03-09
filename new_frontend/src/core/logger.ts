import { isDevelopMode } from "./constants";

class Logger {
  log(...args: any[]) {
    if (isDevelopMode) {
      console.log(...args);
    } else {
      // log somewhere else
    }
  }

  warn(...args: any[]) {
    if (isDevelopMode) {
      console.warn(args);
    } else {
      // log somewhere else
    }
  }

  error(...args: any[]) {
    if (isDevelopMode) {
      console.error(args);
    } else {
      // log somewhere else
    }
  }

  table(...args: any[]) {
    if (isDevelopMode) {
      console.error(args);
    } else {
      // log somewhere else
    }
  }
}

const logger = new Logger();

export default logger;

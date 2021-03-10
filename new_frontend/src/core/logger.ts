import { isDevelopMode } from "../config/constants";

class Logger {
  log(...args: unknown[]) {
    if (isDevelopMode) {
      console.log(...args);
    } else {
      // log somewhere else
    }
  }

  warn(...args: unknown[]) {
    if (isDevelopMode) {
      console.warn(...args);
    } else {
      // log somewhere else
    }
  }

  error(...args: unknown[]) {
    if (isDevelopMode) {
      console.error(...args);
    } else {
      // log somewhere else
    }
  }

  table(...args: unknown[]) {
    if (isDevelopMode) {
      console.error(...args);
    } else {
      // log somewhere else
    }
  }
}

const logger = new Logger();

export default logger;

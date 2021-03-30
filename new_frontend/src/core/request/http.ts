import axios, { AxiosInstance } from "axios";
import urlResolver from "../urlResolver";
import { parseResponse } from "@/utility";
import logger from "../logger";

export class HttpRequest {
  private _resolver: Promise<AxiosInstance>;

  constructor(configUrl: string, defaultUrl: string, token?: string) {
    this._resolver = urlResolver(configUrl, defaultUrl).then((url: string) => {
      const axiosInstance = axios.create();
      axiosInstance.defaults.transformResponse = (data) =>
        parseResponse(JSON.parse(data));

      axiosInstance.defaults.baseURL = url;
      axiosInstance.defaults.headers.common["Content-Type"] =
        "application/json";

      if (token) {
        axiosInstance.defaults.headers.common[
          "Authorization"
        ] = `Bearer ${token}`;
      }

      axiosInstance.defaults.params = {};

      return axiosInstance;
    });
  }

  async setConfig(key: string, value: string) {
    const axiosInstance = await this._resolver;
    axiosInstance.defaults.params[key] = value;
  }

  async get<T extends unknown>(path: string) {
    const axiosInstance = await this._resolver;
    const result = await axiosInstance.get<T>(path);
    return result.data;
  }

  async delete<T extends unknown>(path: string) {
    const axiosInstance = await this._resolver;
    const result = await axiosInstance.delete<T>(path);
    return result.data;
  }

  async post<T extends unknown>(path: string, payload: unknown) {
    const axiosInstance = await this._resolver;
    const result = await axiosInstance.post<T>(path, payload);
    return result.data;
  }

  async patch<T extends unknown>(path: string, payload: unknown) {
    const axiosInstance = await this._resolver;
    const result = await axiosInstance.patch<T>(path, payload);
    return result.data;
  }

  async put<T extends unknown>(path: string, payload: unknown) {
    const axiosInstance = await this._resolver;
    const result = await axiosInstance.put<T>(path, payload);
    return result.data;
  }
}

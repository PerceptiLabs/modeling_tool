import axios, { AxiosInstance } from "axios";
import urlResolver from "../urlResolver";

export class HttpRequest {
  private _resolver: Promise<AxiosInstance>;

  constructor(
    configUrl: string,
    defaultUrl: string,
    token?: string
  ) {
    this._resolver = urlResolver(configUrl, defaultUrl).then((url: string) => {
      const axiosInstance = axios.create();

      axiosInstance.defaults.baseURL = url;
      axiosInstance.defaults.headers.common["Content-Type"] =
        "application/json";

      if (token) {
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`
      }

      return axiosInstance;
    });
  }

  async get<T extends any>(path: string) {
    const requestor = await this._resolver;
    const result = await requestor.get<T>(path);
    return result.data;
  }

  async delete<T extends any>(path: string) {
    const requestor = await this._resolver;
    const result = await requestor.delete<T>(path);
    return result.data;
  }

  async post<T extends any>(path: string, payload: any) {
    const requestor = await this._resolver;
    const result = await requestor.post<T>(path, payload);
    return result.data;
  }

  async patch<T extends any>(path: string, payload: any) {
    const requestor = await this._resolver;
    const result = await requestor.patch<T>(path, payload);
    return result.data;
  }

  async put<T extends any>(path: string, payload: any) {
    const requestor = await this._resolver;
    const result = await requestor.put<T>(path, payload);
    return result.data;
  }
}

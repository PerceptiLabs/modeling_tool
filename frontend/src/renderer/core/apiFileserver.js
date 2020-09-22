import axios            from 'axios'
import { objectToQueryParams } from '@/core/helpers'
import { FILE_SERVER_BASE_URL } from '@/core/constants'

const tokenEndpoint = 'static/token';

const fileServerHttpReqest =  axios.create();
fileServerHttpReqest.defaults.baseURL = FILE_SERVER_BASE_URL
fileServerHttpReqest.defaults.headers.common["Content-Type"] = `application/json`;
fileServerHttpReqest.defaults.params = {}
fileServerHttpReqest.defaults.params['token'] = process.env.PL_FILE_SERVING_TOKEN

if (!process.env.PL_FILE_SERVING_TOKEN) {
  // This section is for when the frontend is built as static files.
  // (process.env is not available then)
  axios.get(tokenEndpoint)
    .then(response => {
      fileServerHttpReqest.defaults.params['token'] = response.data;
    });
}

export const importRepositoryFromGithub = (data) => {
  const queryParams = objectToQueryParams(data);
  return fileServerHttpReqest.post(`/github/import?${queryParams}`, data);
}

export const exportAsGithubRepository = (data) => {
  const queryParams = objectToQueryParams(data);
  return fileServerHttpReqest.post(`/github/export?${queryParams}`, data)
}

export const createIssueInGithub = (params, data) => {
  const queryParams = objectToQueryParams(params);
  return fileServerHttpReqest.post(`/github/issue?${queryParams}`, data)
}
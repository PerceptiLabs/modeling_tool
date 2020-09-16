import axios            from 'axios'
import { objectToQueryParams } from '@/core/helpers'
import { FILE_SERVER_BASE_URL } from '@/core/constants'


const fileServerHttpReqest =  axios.create();
fileServerHttpReqest.defaults.baseURL = FILE_SERVER_BASE_URL
fileServerHttpReqest.defaults.headers.common["Content-Type"] = `application/json`;
fileServerHttpReqest.defaults.params = {}
fileServerHttpReqest.defaults.params['token'] = process.env.PL_FILE_SERVING_TOKEN


export const importRepositoryFromGithub = (data) => {
  const queryParams = objectToQueryParams(data);
  return fileServerHttpReqest.post(`/github/import?${queryParams}`, data);
}

export const exportAsGithubRepository = (data) => {
  const queryParams = objectToQueryParams(data);
  return fileServerHttpReqest.post(`/github/export?${queryParams}`, data)
}

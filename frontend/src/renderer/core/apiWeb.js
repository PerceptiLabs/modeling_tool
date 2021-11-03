import store from '@/store'
import { stringifyNetworkObjects } from '@/core/helpers';
import { whenUrlIsResolved } from '@/core/urlResolver';
import { KERNEL_BASE_URL } from '@/core/constants'
import { KERNEL_URL_CONFIG_PATH }   from "@/core/constants";
import { KERNEL_VERSION_CONFIG_PATH }   from "@/core/constants";
import { whenVersionIsResolved } from '@/core/versionResolver';
import { renderingKernel }  from "@/core/apiRenderingKernel.js";


function calcTime(stop, start, name, nameComp) {
  let time = stop - start;
  console.log(`${name}`, `${nameComp}` , `${time}ms`);
}

const kernelUrlPromise = Promise.all([whenUrlIsResolved(KERNEL_URL_CONFIG_PATH, KERNEL_BASE_URL), whenVersionIsResolved(KERNEL_VERSION_CONFIG_PATH)]).then(([kernel_url]) => {
  return kernel_url;
})

function coreRequest(data, path, no, name) {
  console.error("coreRequest is Deprecated!")
  return Promise.resolve();
}

const openWS = null;
const closeWS = null;


export {coreRequest, openWS, closeWS};

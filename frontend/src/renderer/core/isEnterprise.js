import { IS_ENTERPRISE_CONFIG_PATH } from "@/core/constants";
// Create a promise that fetches a is_enterprise from the server and returns boolean value


export const whenInEnterprise = () => {
  return new Promise((resolve) => {
    fetch(IS_ENTERPRISE_CONFIG_PATH)
    .then(response => response.text())
    .then(result =>{
      if (result.indexOf('true') >= 0){
        resolve(true)
      }
      else if (result.indexOf('html') >= 0){
        // in debug mode we can get html from the npm dev server. Be nice about it
        resolve(false)
      }
      else if (result.indexOf('false') >= 0){
        resolve(false)
      }
      else {
        // anything except true should get reject
        resolve(false)
      }
    })
    .catch(error => {
      resolve(false)
      console.log(error)
    })
  });
}
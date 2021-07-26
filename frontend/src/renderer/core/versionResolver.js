import { whenInEnterprise } from '@/core/isEnterprise';

// for fileserver we need to create a token param with the urlpath: {url}?token={FILESERVER_TOKEN}

export const whenVersionIsResolved = (urlPath) => {
    return new Promise((resolve, reject) => {
      whenInEnterprise().then((isEnterprise) => {
        if(isEnterprise){  
          fetch(urlPath)
          .then(response => response.text())
          .then(result => {
            if (result.indexOf('true') >= 0){
              resolve()
            }
            else {
              // anything except true should get reject as we already checked it's enterprise
              reject()
            }
          })
          .catch(error => {
            resolve()
            console.log(error)
          })
        }
        else{
          resolve()
        }
      })
    });
  }

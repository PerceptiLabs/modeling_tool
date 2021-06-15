// for fileserver we need to create a token param with the urlpath: {url}?token={FILESERVER_TOKEN}

export const whenVersionIsResolved = (urlPath) => {
    return new Promise((resolve, reject) => {
      fetch(urlPath)
      .then(response => response.text())
      .then(result => {
        if (result.indexOf('true') >= 0){
          resolve()
        }
        else if (result.indexOf('html') >= 0){
          // in debug mode we can get html from the npm dev server. Be nice about it
          resolve()
        }
        else if (result.indexOf('false') >= 0){
          reject()
        }
        else {
          // anything except true should get reject
          reject()
        }
      })
      .catch(error => {
        resolve()
        console.log(error)
      })
    });
  }
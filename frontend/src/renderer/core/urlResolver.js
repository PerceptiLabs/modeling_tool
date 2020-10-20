

// Create a promise that fetches a url from a file on the server or returns a default
// URLs are determined by the following precedence:
// 1. the <svc>_url file
// 2. Hard-coded localhost:<port> 


export const whenUrlIsResolved = (urlPath, dflt) => {
  return new Promise(resolve => {
    fetch(urlPath)
    .then(response => response.text())
    .then(fetched => {
      if (!fetched){
        resolve(dflt);
      } else if (fetched.indexOf('html') >= 0){
        // in debug mode we can get html from the npm dev server. Be nice about it
        resolve(dflt)
      } else {
        resolve(fetched)
      }
    })
    .catch(error => {
      resolve(dflt);
    })
  });
}


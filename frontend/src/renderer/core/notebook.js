export const notebookActions = (function() {

  let notebookServer = {
    url: '',
    notebookName: '',
    token: ''
  };

  const publicMethods = {};

  publicMethods.init = function({ url, notebookName, token}) {
    notebookServer.url = url;
    notebookServer.notebookName = notebookName;
    notebookServer.token = token;
  }

  publicMethods.getNotebookContents = function() {
    const notebookContentsUrl =
      notebookServer.url +
      "/api/contents/" +
      notebookServer.notebookName +
      notebookServer.token;
    return fetch(notebookContentsUrl)
      .then(response => response.json())
      .then(json => {
        return json;
      });
  }

  publicMethods.getKernelSpecs = function() {
    const kernelsUrl =
      this.notebookServer.url +
      "/api/kernelspecs" +
      this.notebookServer.token;

    return fetch(kernelsUrl)
    .then(response => response.json())
    .then(json => {
      return json;
    });
  }

  publicMethods.getSessions = function() {
    const kernelsUrl =
      notebookServer.url +
      "/api/sessions" +
      notebookServer.token;
    
    return fetch(kernelsUrl)
    .then(response => response.json())
    .then(json => {
      // console.log('sessions', json);
      const currentSession = json.find(s => s.name == notebookServer.notebookName);
      if (!currentSession) { 
        startSession();
      }
    });
  }

  publicMethods.startSession = function() {
    const payload = {
      path: notebookServer.notebookName,
      type: 'notebook',
      name: notebookServer.notebookName,
      kernel: {
        id: null, 
        name: 'python3'
      }
    };

    const kernelsUrl =
      notebookServer.url +
      "/api/sessions" +
      notebookServer.token;
    return fetch(kernelsUrl, { 
      method: 'POST',
      body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(json => {
      console.log('POST sessions', json);
      return json;
    })
    .catch(error => {
      return error;
    });
  }
  
  return publicMethods;

})();


export default {
    notebookActions
}
self.addEventListener('message', function(e) {
  if(e.data === 'close') {
    self.close();
  }
  else {
    for (var i = 0; i < e.data.xLength; i++) {
      e.data.model.xAxis.data.push(i);
    }
    postMessage(e.data.model);
  }
}, false);

self.addEventListener('message', function(message) {
  let maxItems = 400;

  switch (message.data) {
    case 'close':
      self.close();
      break;
    default:
      let model = message.data.model;
      let xLength = message.data.xLength;
      var nFilter;

      if(xLength > maxItems*2) {
        nFilter = Math.ceil(xLength / maxItems);
        let filteredXAxis = false;
        for (let line of model.series) {
          let resultMaxItems = [];

          for (let i = 0; i < xLength; i=i+nFilter) {
            if(!filteredXAxis) {
              model.xAxis.data.push(i)
            }
            resultMaxItems.push(line.data[i])
          }
          filteredXAxis = true;
          line.data = resultMaxItems;
        }
      }
      else if(xLength > maxItems && xLength <= maxItems*2) {

        nFilter = Math.ceil(xLength / (xLength - maxItems));

        for (let line of model.series) {
          let resultMaxItems = line.data.filter((item, index)=> index%nFilter);
          line.data = resultMaxItems;
        }
        createXAxis(model.xAxis.data, xLength);
        let filteredXAxis = model.xAxis.data.filter((item, index)=> index%nFilter);
        model.xAxis.data = filteredXAxis;
      }
      else {
        createXAxis(model.xAxis.data, xLength)
      }

      postMessage(model);

      function createXAxis(data, xLength) {
        for (let i = 0; i < xLength; i++) {
          data.push(i);
        }
      }
  }
}, false);

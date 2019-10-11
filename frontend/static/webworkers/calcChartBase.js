self.addEventListener('message', function(message) {
  let maxItems = 475;

  switch (message.data) {
    case 'close':
      self.close();
      break;
    default:
      let model = message.data.model;
      let xLength = message.data.xLength;
      console.log(JSON.parse(JSON.stringify(model.series)));
      createXAxis(model.xAxis.data, xLength);
      filteredSeriesData(model);
      //console.log(model);
      postMessage(model);
  }
  function createXAxis(data, xLength) {
    let nFilter;
    console.log(data);
    if(xLength > maxItems*2) {
      nFilter = Math.ceil(xLength / maxItems);
      for (let i = 1; i <= xLength; i=i+nFilter) {
        data.push(i);
      }
    }
    else if(xLength > maxItems && xLength <= maxItems*2) {
      nFilter = Math.round(xLength / (xLength - maxItems));
      for (let i = 1; i <= xLength; i++) {
        if(i % nFilter) data.push(i);
      }
    }
    else {
      for (let i = 1; i <= xLength; i++) {
        data.push(i);
      }
    }
    console.log(data);
    if(data[0] !== 1) data.unshift(1);
    if(data[data.length-1] !== xLength) data.push(xLength);
    console.log(data);
  }
  function filteredSeriesData(model) {
    let newChartData = [];
    model.series.forEach((chart)=> {
      model.xAxis.data.forEach((indexPoint)=> {
        newChartData.push(chart.data[indexPoint - 1])
      });
      chart.data = newChartData
    });
  }
}, false);

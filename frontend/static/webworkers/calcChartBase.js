self.addEventListener('message', function(message) {
  let maxItems = 475;

  switch (message.data) {
    case 'close':
      self.close();
      break;
    default:
      let model = message.data.model;
      let xLength = message.data.xLength;
      //console.log(JSON.parse(JSON.stringify(model)));
      createXAxis(model.xAxis.data, xLength);
      filteredSeriesData(model);
      //console.log(model);
      postMessage(model);
  }
  function createXAxis(data, xLength) {
    let nFilter;
    if(xLength > maxItems*2) {
      nFilter = Math.ceil(xLength / maxItems);
      for (let i = 0; i < xLength; i=i+nFilter) {
        data.push(i);
      }
    }
    else if(xLength > maxItems && xLength <= maxItems*2) {
      nFilter = Math.round(xLength / (xLength - maxItems));
      for (let i = 0; i < xLength; i++) {
        if(i % nFilter) data.push(i);
      }
    }
    else {
      for (let i = 0; i < xLength; i++) {
        data.push(i);
      }
    }
    // if(data[0] !== 0) data.unshift(0);
    // if(data.length > maxItems) {
    //   if (data[data.length - 1] !== xLength - 1) data.push(xLength - 1);
    // }
  }
  function filteredSeriesData(model) {
    model.series.forEach((chart)=> {
      let newChartData = [];
      model.xAxis.data.forEach((indexPoint)=> {
        newChartData.push(chart.data[indexPoint])
      });
      chart.data = newChartData
    });
  }
}, false);

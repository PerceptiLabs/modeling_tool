const dataBar = {
  tooltip: {},
  legend: {
    data: [{name: 'Sales', icon: 'circle'}, 'Buy']
  },
  xAxis: {
    boundaryGap: true,
    data: ["0", "1", "2"]
  },
  // yAxis: {
  //   data: ["0", "1"]
  // },
  series: [
    {
      name: 'Sales',
      type: 'line',
      data: [5, 20, 36],
      lineStyle: {
        color: '#ff00ff'
      }
    },
    {
      name: 'Buy',
      type: 'line',
      data: [1, 2, 3, 36, 20, 20, 20],
      lineStyle: {
        color: '#ffff00'
      }
    }
  ]
}

export default dataBar


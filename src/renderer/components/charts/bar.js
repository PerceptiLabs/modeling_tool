const dataBar = {
  tooltip: {},
  legend: {
    data: ['Sales', 'Buy']
  },
  xAxis: {
    boundaryGap: true,
    data: ["0", "1", "2"]
  },
  yAxis: {
    data: ["0", "1"]
  },
  series: [
    {
      name: 'Sales',
      type: 'bar',
      data: [5, 20, 36]
    },
    {
      name: 'Buy',
      type: 'bar',
      data: [0, 0, 0, 36, 20, 20, 20]
    }
  ]
}

export default dataBar


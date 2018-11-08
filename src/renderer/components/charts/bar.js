const dataBar = {
  tooltip: {},
  legend: {
    data:['Sales', 'Buy']
  },
  xAxis: {
    boundaryGap: true,
      data: ["shirt","cardign","chiffon shirt","pants","heels","socks"]
  },
  yAxis: {},
  series: [
    {
      name: 'Sales',
      type: 'bar',
      data: [5, 20, 36, 10, 10, 20]
    },
    {
      name: 'Buy',
      type: 'bar',
      data: [15, 2, 6, 30, 20, 20]
    }
  ]
}

export default dataBar

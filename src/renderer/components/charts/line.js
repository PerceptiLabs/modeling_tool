// const dataLine = {
//   tooltip: {},
//   xAxis: {
//     data: ['Geek', 'Potato', 'Cool', 'Cat', 'Dog'],
//   },
//   yAxis: {},
//   series: [
//     {
//       type: 'line',
//       data: [0.1, 0.5, 0.6, .99, .75],
//     },
//     {
//       type: 'line',
//       data: [0.51, 0.15, 0.96, .199, .175],
//     },
//     {
//       name: 'Sales',
//       type: 'bar',
//       data: [5, 20, 36, 10, 10, 20]
//     },
//     {
//       name: 'Buy',
//       type: 'bar',
//       data: [15, 2, 6, 30, 20, 20]
//     }
//   ]
// }

const dataLine = [
  {
    type: 'line',
    data: [1, 5, 6, 9, 7],
  },
  {
    type: 'line',
    data: [5, 10, 6, 9, 15],
  },
  // {
  //   name: 'Sales',
  //   type: 'bar',
  //   data: [5, 20, 36, 10, 10, 20]
  // },
  // {
  //   name: 'Buy',
  //   type: 'bar',
  //   data: [15, 2, 6, 30, 20, 20]
  // },
  // {
  //   name: 'Sales',
  //   type: 'bar',
  //   data: [5, 20, 36, 10, 10, 20]
  // },
  {
    name: 'Buy',
    type: 'bar',
    data: [15, 2, 6, 30, 20, 20]
  },
  {
    //symbolSize: 20,
    type: 'scatter',
    data: [
      [5.0, 0]
    ],
  }
]

export default dataLine

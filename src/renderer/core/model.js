//For example answer DataData

const modelAnswer = {
  length: 123132, //it is content-length from the header
  message: {
    Data: {
      legend: {
        data: ['Label Name'] //array must have all 'name's from 'series' array
      },
      series: [{
        name: 'Label Name',
        data: [1,2,34,4,5,5,6,67,78,8],
        type: "line",
        lineStyle: {      //---------
          color: '#123456'// it is custom line color
        }                 //---------
      }]
    }
  }
}

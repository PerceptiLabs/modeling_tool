/*building in http://echarts.baidu.com/theme-builder/*/

import Vue from 'vue'
import ECharts from 'vue-echarts/components/ECharts'
import 'echarts-gl/dist/echarts-gl.js'

ECharts.registerTheme('light', {
  grid: {
    top: '20',
    bottom: '30',
    right: '10',
    left: '30',
  },
  "color": [
    "#6b8ff7",
    "#FECF73",
    "#46d65d",
    "#fe7373",
    "#e273fe",
    "#61e6ee",
    "#d3dffe",
    "#bda29a",
    "#6167ee",
    "#ca8622",
    "#c4ccd3"
  ],
  "backgroundColor": "#FFF",
  "textStyle": {},
  "title": {
    "textStyle": {
      "color": "#6185EE"
    },
    "subtextStyle": {
      "color": "#8b8b9c"
    }
  },
  "categoryAxis": {
    "boundaryGap": false,
    "nameTextStyle": {
      color: '#5D5D64',
    },
    "axisLine": {
      "show": true,
      "lineStyle": {
        "color": "#E2E2EA"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#E2E2EA"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#5D5D64"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#E2E2EA"
        ]
      }
    },
    "splitArea": {
      "show": false,
      "areaStyle": {
        "color": [
          "rgba(250,250,250,0.3)",
          "rgba(200,200,200,0.3)"
        ]
      }
    }
  },
  "valueAxis": {
    "axisLine": {
      "show": true,
      "lineStyle": {
        "color": "#E2E2EA"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#E2E2EA"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#5D5D64"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#E2E2EA"
        ]
      }
    },
    "splitArea": {
      "show": false,
      "areaStyle": {
        "color": [
          "rgba(250,250,250,0.3)",
          "rgba(200,200,200,0.3)"
        ]
      }
    }
  },
  "logAxis": {
    "axisLine": {
      "show": true,
      "lineStyle": {
        "color": "#E2E2EA"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#E2E2EA"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#5D5D64"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#E2E2EA"
        ]
      }
    },
    "splitArea": {
      "show": false,
      "areaStyle": {
        "color": [
          "rgba(250,250,250,0.3)",
          "rgba(200,200,200,0.3)"
        ]
      }
    }
  },
  "timeAxis": {
    "axisLine": {
      "show": true,
      "lineStyle": {
        "color": "#E2E2EA"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#E2E2EA"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#5D5D64"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#E2E2EA"
        ]
      }
    },
    "splitArea": {
      "show": false,
      "areaStyle": {
        "color": [
          "rgba(250,250,250,0.3)",
          "rgba(200,200,200,0.3)"
        ]
      }
    }
  },
  "toolbox": {
    "iconStyle": {
      "normal": {
        "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderColor": "#8b8b9c"
      }
    }
  },
  "legend": {
    "top": "0",
    "textStyle": {
      "color": "#5D5D64"
    },

  },
  "tooltip": {
    "axisPointer": {
      "lineStyle": {
        "color": "#e1e1e1",
        "width": 1
      },
      "crossStyle": {
        "color": "#e1e1e1",
        "width": 1
      }
    }
  },
  "timeline": {
    "lineStyle": {
      "color": "#6b8ff7",
      "width": 1
    },
    "itemStyle": {
      "normal": {
        "color": "#293c55",
        "borderWidth": 1
      },
      "emphasis": {
        "color": "#6b8ff7"
      }
    },
    "controlStyle": {
      "normal": {
        "color": "#e1e1e1",
        "borderColor": "#e1e1e1",
        "borderWidth": 0.5
      },
      "emphasis": {
        "color": "#e1e1e1",
        "borderColor": "#e1e1e1",
        "borderWidth": 0.5
      }
    },
    "checkpointStyle": {
      "color": "#6b8ff7",
      "borderColor": "rgba(255,255,255,0.5)"
    },
    "label": {
      "normal": {
        "textStyle": {
          "color": "#5D5D64"
        }
      },
      "emphasis": {
        "textStyle": {
          "color": "#44444F"
        }
      }
    }
  },
  "visualMap": {
    "color": [
      "#4065C1",
      "#4B70D0",
      "#567ADF",
      "#6185EE",
      "#86A2F4",
      "#ABBEF9",
      "#D0DBFF",
      "transparent"
    ],
    textStyle: {
      color: '#5D5D64'
    },
    "calculable": true,
    itemWidth: 10,
  },
  "dataZoom": {
    "backgroundColor": "#FFF",
    "dataBackgroundColor": "#e1e1e1",
    "fillerColor": "rgba(167,183,204,0.4)",
    "handleColor": "#a7b7cc",
    "handleSize": "100%",
    "textStyle": {
      "color": "#5D5D64"
    }
  },
  "markPoint": {
    "label": {
      "normal": {
        "textStyle": {
          "color": "#5D5D64"
        }
      },
      "emphasis": {
        "textStyle": {
          "color": "#44444F"
        }
      }
    }
  },
  /* Types */
  "line": {
    "itemStyle": {
      "normal": {
        "borderWidth": "10"
      }
    },
    "lineStyle": {
      "normal": {
        "width": "3"
      }
    },
    "symbolSize": "0", //show dots
      "symbol": "emptyCircle", //Circle
      "smooth": true
  },
  "radar": {
    "itemStyle": {
      "normal": {
        "borderWidth": "10"
      }
    },
    "lineStyle": {
      "normal": {
        "width": "3"
      }
    },
    "symbolSize": "2",
      "symbol": "emptyCircle",
      "smooth": true
  },
  "bar": {
    "barWidth": '8px',
    "barGap": '100%',
    "xAxis": {
      'boundaryGap': true
    },
    "itemStyle": {
      "normal": {
        "barBorderWidth": 0,
        "barBorderColor": "#e1e1e1"
      },
      "emphasis": {
        "barBorderWidth": 0,
        "barBorderColor": "#e1e1e1"
      }
    }
  },
  "pie": {
    "radius": '60%',
    "center": ['50%', '50%'],
  },
  "scatter": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "boxplot": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "parallel": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "sankey": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "funnel": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "gauge": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "candlestick": {
    "itemStyle": {
      "normal": {
        "color": "#46d65d",
          "color0": "#fe7373",
          "borderColor": "#46d65d",
          "borderColor0": "#fe7373",
          "borderWidth": "2"
      }
    }
  },
  "graph": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    },
    "lineStyle": {
      "normal": {
        "width": 1,
          "color": "#aaa"
      }
    },
    "symbolSize": "2",
      "symbol": "emptyCircle",
      "smooth": true,
      "color": [
      "#6b8ff7",
      "#f7e96b",
      "#46d65d",
      "#fe7373",
      "#e273fe",
      "#61e6ee",
      "#d3dffe",
      "#bda29a",
      "#6167ee",
      "#ca8622",
      "#c4ccd3"
    ],
      "label": {
      "normal": {
        "textStyle": {
          "color": "#23252a"
        }
      }
    }
  },
  "map": {
    "itemStyle": {
      "normal": {
        "areaColor": "#e1e1e1",
          "borderColor": "#4d556a",
          "borderWidth": 0.5
      },
      "emphasis": {
        "areaColor": "#6b8ff7",
          "borderColor": "#444",
          "borderWidth": 1
      }
    },
    "label": {
      "normal": {
        "textStyle": {
          "color": "#000000"
        }
      },
      "emphasis": {
        "textStyle": {
          "color": "#000000"
        }
      }
    }
  },
  "geo": {
    "itemStyle": {
      "normal": {
        "areaColor": "#e1e1e1",
          "borderColor": "#4d556a",
          "borderWidth": 0.5
      },
      "emphasis": {
        "areaColor": "#6b8ff7",
          "borderColor": "#444",
          "borderWidth": 1
      }
    },
    "label": {
      "normal": {
        "textStyle": {
          "color": "#000000"
        }
      },
      "emphasis": {
        "textStyle": {
          "color": "#000000"
        }
      }
    }
  },
  "heatmap": {
    "emphasis": {
      "itemStyle": {
        "borderColor": '#e1e1e1',
        "borderWidth": 2
      }
    },
    progressive: 1000,
    animation: false,
    inRange: {
      color: ['#DD2000', '#009000' ]
    }
  },
  "scatter3D": {
    "itemStyle": {
      "borderWidth": 1,
      "borderColor": "#fff"
    },
    "emphasis": {
      "itemStyle": {
        "color": "#e1e1e1"
      }
    },
  },
  "grid3D": {
    temporalSuperSampling: {
      enable: true
    },
    "axisLine": {
      "lineStyle": {
        "color": "#3c3c4c",
      }
    },
    axisLabel: {
      textStyle: {
        color: "#e1e1e1"
      }
    },
    "axisPointer": {
      "lineStyle": {
        "color": "#ffbd67"
      }
    },
    "viewControl": {},
    splitLine: {
      lineStyle: {
        color: "#3c3c4c"
      }
    }
  },
  "xAxis3D": {
    "type": "value",
    "nameTextStyle": {
      "color": "#e1e1e1",
    }
  },
  "yAxis3D": {
    "type": "value",
    nameTextStyle: {
      color: "#e1e1e1",
    }
  },
  "zAxis3D": {
    "type": "value",
    nameTextStyle: {
      color: "#e1e1e1",
    }
  },
});

ECharts.registerTheme('dark', {
  grid: {
    top: '30',
    bottom: '30',
    right: '10',
    left: '30',
  },
  "color": [
    "#6b8ff7",
    "#FECF73",
    "#46d65d",
    "#fe7373",
    "#e273fe",
    "#61e6ee",
    "#d3dffe",
    "#bda29a",
    "#6167ee",
    "#ca8622",
    "#c4ccd3"
  ],
  "backgroundColor": "#2B2C31",
  "textStyle": {},
  "title": {
    "textStyle": {
      "color": "#6185EE"
    },
    "subtextStyle": {
      "color": "#8b8b9c"
    }
  },
  "categoryAxis": {
    "boundaryGap": false,
    "nameTextStyle": {
      color: '#FFFFFF',
    },
    "axisLine": {
      "show": true,
      "lineStyle": {
        "color": "#494A4F"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#494A4F"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#FFFFFF"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#494A4F"
        ]
      }
    },
    "splitArea": {
      "show": false,
      "areaStyle": {
        "color": [
          "rgba(250,250,250,0.3)",
          "rgba(200,200,200,0.3)"
        ]
      }
    }
  },
  "valueAxis": {
    "axisLine": {
      "show": true,
      "lineStyle": {
        "color": "#494A4F"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#494A4F"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#FFFFFF"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#494A4F"
        ]
      }
    },
    "splitArea": {
      "show": false,
      "areaStyle": {
        "color": [
          "rgba(250,250,250,0.3)",
          "rgba(200,200,200,0.3)"
        ]
      }
    }
  },
  "logAxis": {
    "axisLine": {
      "show": true,
      "lineStyle": {
        "color": "#494A4F"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#494A4F"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#FFFFFF"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#494A4F"
        ]
      }
    },
    "splitArea": {
      "show": false,
      "areaStyle": {
        "color": [
          "rgba(250,250,250,0.3)",
          "rgba(200,200,200,0.3)"
        ]
      }
    }
  },
  "timeAxis": {
    "axisLine": {
      "show": true,
      "lineStyle": {
        "color": "#494A4F"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#494A4F"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#FFFFFF"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#494A4F"
        ]
      }
    },
    "splitArea": {
      "show": false,
      "areaStyle": {
        "color": [
          "rgba(250,250,250,0.3)",
          "rgba(200,200,200,0.3)"
        ]
      }
    }
  },
  "toolbox": {
    "iconStyle": {
      "normal": {
        "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderColor": "#8b8b9c"
      }
    }
  },
  "legend": {
    "top": "0",
    "textStyle": {
      "color": "#FFFFFF"
    },

  },
  "tooltip": {
    "axisPointer": {
      "lineStyle": {
        "color": "#e1e1e1",
        "width": 1
      },
      "crossStyle": {
        "color": "#e1e1e1",
        "width": 1
      }
    }
  },
  "timeline": {
    "lineStyle": {
      "color": "#6b8ff7",
      "width": 1
    },
    "itemStyle": {
      "normal": {
        "color": "#293c55",
        "borderWidth": 1
      },
      "emphasis": {
        "color": "#6b8ff7"
      }
    },
    "controlStyle": {
      "normal": {
        "color": "#e1e1e1",
        "borderColor": "#e1e1e1",
        "borderWidth": 0.5
      },
      "emphasis": {
        "color": "#e1e1e1",
        "borderColor": "#e1e1e1",
        "borderWidth": 0.5
      }
    },
    "checkpointStyle": {
      "color": "#6b8ff7",
      "borderColor": "rgba(255,255,255,0.5)"
    },
    "label": {
      "normal": {
        "textStyle": {
          "color": "#FFFFFF"
        }
      },
      "emphasis": {
        "textStyle": {
          "color": "#FFFFFF"
        }
      }
    }
  },
  "visualMap": {
    "color": [
      "#4065C1",
      "#4B70D0",
      "#567ADF",
      "#6185EE",
      "#86A2F4",
      "#ABBEF9",
      "#D0DBFF",
      "transparent"
    ],
    textStyle: {
      color: '#FFFFFF'
    },
    "calculable": true,
    itemWidth: 10,
  },
  "dataZoom": {
    "backgroundColor": "#2B2C31",
    "dataBackgroundColor": "#e1e1e1",
    "fillerColor": "rgba(167,183,204,0.4)",
    "handleColor": "#a7b7cc",
    "handleSize": "100%",
    "textStyle": {
      "color": "#FFFFFF"
    }
  },
  "markPoint": {
    "label": {
      "normal": {
        "textStyle": {
          "color": "#FFFFFF"
        }
      },
      "emphasis": {
        "textStyle": {
          "color": "#FFFFFF"
        }
      }
    }
  },
  /* Types */
  "line": {
    "itemStyle": {
      "normal": {
        "borderWidth": "10"
      }
    },
    "lineStyle": {
      "normal": {
        "width": "3"
      }
    },
    "symbolSize": "0", //show dots
      "symbol": "emptyCircle", //Circle
      "smooth": true
  },
  "radar": {
    "itemStyle": {
      "normal": {
        "borderWidth": "10"
      }
    },
    "lineStyle": {
      "normal": {
        "width": "3"
      }
    },
    "symbolSize": "2",
      "symbol": "emptyCircle",
      "smooth": true
  },
  "bar": {
    "barWidth": '8px',
    "barGap": '100%',
    "xAxis": {
      'boundaryGap': true
    },
    "itemStyle": {
      "normal": {
        "barBorderWidth": 0,
        "barBorderColor": "#e1e1e1"
      },
      "emphasis": {
        "barBorderWidth": 0,
        "barBorderColor": "#e1e1e1"
      }
    }
  },
  "pie": {
    "radius": '60%',
    "center": ['50%', '50%'],
  },
  "scatter": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "boxplot": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "parallel": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "sankey": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "funnel": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "gauge": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      },
      "emphasis": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    }
  },
  "candlestick": {
    "itemStyle": {
      "normal": {
        "color": "#46d65d",
          "color0": "#fe7373",
          "borderColor": "#46d65d",
          "borderColor0": "#fe7373",
          "borderWidth": "2"
      }
    }
  },
  "graph": {
    "itemStyle": {
      "normal": {
        "borderWidth": 0,
          "borderColor": "#e1e1e1"
      }
    },
    "lineStyle": {
      "normal": {
        "width": 1,
          "color": "#aaa"
      }
    },
    "symbolSize": "2",
      "symbol": "emptyCircle",
      "smooth": true,
      "color": [
      "#6b8ff7",
      "#f7e96b",
      "#46d65d",
      "#fe7373",
      "#e273fe",
      "#61e6ee",
      "#d3dffe",
      "#bda29a",
      "#6167ee",
      "#ca8622",
      "#c4ccd3"
    ],
      "label": {
      "normal": {
        "textStyle": {
          "color": "#23252a"
        }
      }
    }
  },
  "map": {
    "itemStyle": {
      "normal": {
        "areaColor": "#e1e1e1",
          "borderColor": "#4d556a",
          "borderWidth": 0.5
      },
      "emphasis": {
        "areaColor": "#6b8ff7",
          "borderColor": "#444",
          "borderWidth": 1
      }
    },
    "label": {
      "normal": {
        "textStyle": {
          "color": "#000000"
        }
      },
      "emphasis": {
        "textStyle": {
          "color": "#000000"
        }
      }
    }
  },
  "geo": {
    "itemStyle": {
      "normal": {
        "areaColor": "#e1e1e1",
          "borderColor": "#4d556a",
          "borderWidth": 0.5
      },
      "emphasis": {
        "areaColor": "#6b8ff7",
          "borderColor": "#444",
          "borderWidth": 1
      }
    },
    "label": {
      "normal": {
        "textStyle": {
          "color": "#000000"
        }
      },
      "emphasis": {
        "textStyle": {
          "color": "#000000"
        }
      }
    }
  },
  "heatmap": {
    "emphasis": {
      "itemStyle": {
        "borderColor": '#e1e1e1',
        "borderWidth": 2
      }
    },
    progressive: 1000,
    animation: false,
    inRange: {
      color: ['#DD2000', '#009000' ]
    }
  },
  "scatter3D": {
    "itemStyle": {
      "borderWidth": 1,
      "borderColor": "#fff"
    },
    "emphasis": {
      "itemStyle": {
        "color": "#e1e1e1"
      }
    },
  },
  "grid3D": {
    temporalSuperSampling: {
      enable: true
    },
    "axisLine": {
      "lineStyle": {
        "color": "#3c3c4c",
      }
    },
    axisLabel: {
      textStyle: {
        color: "#e1e1e1"
      }
    },
    "axisPointer": {
      "lineStyle": {
        "color": "#ffbd67"
      }
    },
    "viewControl": {},
    splitLine: {
      lineStyle: {
        color: "#3c3c4c"
      }
    }
  },
  "xAxis3D": {
    "type": "value",
    "nameTextStyle": {
      "color": "#e1e1e1",
    }
  },
  "yAxis3D": {
    "type": "value",
    nameTextStyle: {
      color: "#e1e1e1",
    }
  },
  "zAxis3D": {
    "type": "value",
    nameTextStyle: {
      color: "#e1e1e1",
    }
  },
});

Vue.component('v-chart', ECharts);

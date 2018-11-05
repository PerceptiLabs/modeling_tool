/*building in http://echarts.baidu.com/theme-builder/*/

import Vue from 'vue'
import ECharts from 'vue-echarts/components/ECharts'
import 'echarts-gl/dist/echarts-gl.js'

ECharts.registerTheme('quantum', {
  grid: {
    top: '20',
    bottom: '30',
    right: '30',
    left: '35',
  },
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
  "backgroundColor": "#23252a",
  "textStyle": {},
  "title": {
    "textStyle": {
      "color": "#e1e1e1"
    },
    "subtextStyle": {
      "color": "#8b8b9c"
    }
  },
  "categoryAxis": {
    "boundaryGap": false,
    "axisLine": {
      "show": true,
      "lineStyle": {
        "color": "#3c3c4c"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#3c3c4c"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#e1e1e1"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#3c3c4c"
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
        "color": "#3c3c4c"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#3c3c4c"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#e1e1e1"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#3c3c4c"
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
        "color": "#3c3c4c"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#3c3c4c"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#e1e1e1"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#3c3c4c"
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
        "color": "#3c3c4c"
      }
    },
    "axisTick": {
      "show": true,
      "lineStyle": {
        "color": "#3c3c4c"
      }
    },
    "axisLabel": {
      "show": true,
      "textStyle": {
        "color": "#e1e1e1"
      }
    },
    "splitLine": {
      "show": true,
      "lineStyle": {
        "color": [
          "#3c3c4c"
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
    "textStyle": {
      "color": "#e1e1e1"
    }
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
          "color": "#e1e1e1"
        }
      },
      "emphasis": {
        "textStyle": {
          "color": "#e1e1e1"
        }
      }
    }
  },
  "visualMap": {
    "color": [
      "#1710c0",
      "#0b9df0",
      "#00fea8",
      "#00ff0d",
      "#f5f811",
      "#f09a09",
      "#fe0300"
    ],
    textStyle: {
      color: '#e1e1e1'
    },
    "calculable": true,
    itemWidth: 10,
  },
  "dataZoom": {
    "backgroundColor": "#23252a",
    "dataBackgroundColor": "#e1e1e1",
    "fillerColor": "rgba(167,183,204,0.4)",
    "handleColor": "#a7b7cc",
    "handleSize": "100%",
    "textStyle": {
      "color": "#e1e1e1"
    }
  },
  "markPoint": {
    "label": {
      "normal": {
        "textStyle": {
          "color": "#23252a"
        }
      },
      "emphasis": {
        "textStyle": {
          "color": "#23252a"
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
    "symbolSize": "10",
      "symbol": "emptyCircle",
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
    barWidth: '8px',
    barGap: '100%',
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
    animation: false
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

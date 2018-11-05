import TextEditable     from '@/components/base/text-editable.vue'
import NetworkField     from '@/components/network-field/network-field.vue'
import GeneralSettings  from "@/components/global-popups/workspace-general-settings.vue";
import GeneralResult    from "@/components/global-popups/workspace-result";
import SelectCoreSide   from "@/components/global-popups/workspace-core-side";
import ChartLine        from "@/components/charts/chart-line";
import ChartBar         from "@/components/charts/chart-bar";
import Chart3d          from "@/components/charts/chart-3d";
import ChartHeatmap     from "@/components/charts/chart-heatmap.vue";

import data3d         from "./3d";
import heat           from "./hear";


export default {
  name: 'WorkspaceContent',
  components: {
    NetworkField,
    TextEditable,
    GeneralSettings,
    GeneralResult,
    SelectCoreSide,
    ChartLine,
    ChartBar,
    'chart-3d': Chart3d,
    ChartHeatmap
  },
  data () {
    return {
      scale: 100,
      optionLine: {
        tooltip: {},
        xAxis: {
          data: ['Geek', 'Potato', 'Cool', 'Cat', 'Dog'],
        },
        yAxis: {},
        series: [
          {
            type: 'line',
            data: [0.1, 0.5, 0.6, .99, .75],
          },
          {
            type: 'line',
            data: [0.51, 0.15, 0.96, .199, .175],
          }
        ]
      },
      optionBar: {
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
      },
      option3d: data3d,
      // option3d: {
      //   tooltip: {},
      //   grid3D: {},
      //   xAxis3D: {},
      //   yAxis3D: {},
      //   zAxis3D: {},
      //   series: [{
      //     type: 'scatter3D',
      //     data: [[-1, -1, -1], [0, 0, 0], [1, 1, 1]],
      //   }]
      // },
      optionHeat: {
        tooltip: {},
        grid: {
          right: 80
        },
        xAxis: {
          type: 'category',
          data: [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            35,
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79,
            80,
            81,
            82,
            83,
            84,
            85,
            86,
            87,
            88,
            89,
            90,
            91,
            92,
            93,
            94,
            95,
            96,
            97,
            98,
            99,
            100,
            101,
            102,
            103,
            104,
            105,
            106,
            107,
            108,
            109,
            110,
            111,
            112,
            113,
            114,
            115,
            116,
            117,
            118,
            119,
            120,
            121,
            122,
            123,
            124,
            125,
            126,
            127,
            128,
            129,
            130,
            131,
            132,
            133,
            134,
            135,
            136,
            137,
            138,
            139,
            140,
            141,
            142,
            143,
            144,
            145,
            146,
            147,
            148,
            149,
            150,
            151,
            152,
            153,
            154,
            155,
            156,
            157,
            158,
            159,
            160,
            161,
            162,
            163,
            164,
            165,
            166,
            167,
            168,
            169,
            170,
            171,
            172,
            173,
            174,
            175,
            176,
            177,
            178,
            179,
            180,
            181,
            182,
            183,
            184,
            185,
            186,
            187,
            188,
            189,
            190,
            191,
            192,
            193,
            194,
            195,
            196,
            197,
            198,
            199,
            200
          ]
        },
        yAxis: {
          type: 'category',
          data: [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            35,
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79,
            80,
            81,
            82,
            83,
            84,
            85,
            86,
            87,
            88,
            89,
            90,
            91,
            92,
            93,
            94,
            95,
            96,
            97,
            98,
            99
          ]
        },
        visualMap: {
          min: 0,
          max: 1,
          top: '10px',
          itemHeight: 300,
          realtime: false,
          left: 'right',
        },
        series: [{
          name: 'Gaussian',
          type: 'heatmap',
          data: heat,
        }]
      }
    }
  },
  mounted() {

  },
  computed: {

    styleScale() {
      return this.scale / 100
    },
    workspace() {
      return this.$store.state.mod_workspace.workspaceContent
    },
    currentNetwork() {
      return this.$store.state.mod_workspace.currentNetwork
    },
    hideSidebar() {
      return this.$store.state.globalView.hideSidebar
    },
    showGlobalSet() {
      return this.$store.state.globalView.globalPopup.showNetSettings
    },
    showGlobalResult() {
      return this.$store.state.globalView.globalPopup.showNetResult
    },
    showStatistics() {
      return this.$store.state.globalView.showStatistics
    },
    showCoreSide() {
      return this.$store.state.globalView.globalPopup.showCoreSideSettings
    },
    appMode() {
      return this.$store.state.globalView.appMode
    },
  },
  methods: {
    // addLayer(e) {
    //   console.log('addLayer')
    //   let layer = {
    //     layerId: e.timeStamp,
    //     layerName: e.target.dataset.layer,
    //     layerChild: null,
    //     componentName: e.target.dataset.component,
    //     meta: {
    //       isVisible: true,
    //       isDraggable: true,
    //       top: e.offsetY - e.target.clientHeight/2,
    //       left: e.offsetX - e.target.clientWidth/2
    //     }
    //   }
    //   this.network.push(layer);
    // },
    deleteTabNetwork(index) {
      this.$store.commit('mod_workspace/DELETE_workspaceTab', index)
    },
    setTabNetwork(index) {
      this.$store.commit('mod_workspace/SET_currentNetwork', index);
      this.$store.commit('globalView/SET_showStatistics', false)
    },
    toggleSidebar () {
      this.$store.commit('globalView/SET_hideSidebar', !this.hideSidebar)
    },
    decScale () {
      if (this.scale < 10) {
        this.scale = 5
      }
      else this.scale = this.scale - 10
    },
    incScale () {
      if (this.scale > 90) {
        this.scale = 100
      }
      else this.scale = this.scale + 10
    },
    resize(newRect, i) {
      //console.log(newRect);
      //console.log(i);
      // this.network[i].meta.top = newRect.top;
      // this.network[i].meta.left = newRect.left;
    },
    onActivated(e) {
      //console.log(e)
    },
    editNetName(newName) {
      this.$store.commit('mod_workspace/SET_networkName', newName);
    },
  }
}

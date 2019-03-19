import requestApi from "@/core/api.js";

const netElementSettingsData = {
  props: {
    layerId: {
      type: String,
      default: ''
    }
  },

  data() {
    return {
      imgData: null,
      imgType: '',
    }
  },

  computed: {
    currentNetworkID() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkID
    },
  },
  methods: {
    getDataImg(type) {
      let theData = {
        reciever: this.currentNetworkID,
        action: 'getDataPlot',
        value: {
          Id: this.layerId,
          Type: type,
          Properties: this.settings
        }
      };
      //console.log('getDataImg', theData);
      const client = new requestApi();
      client.sendMessage(theData)
        .then((data)=> {
          //console.log('answer getDataImg', data);
          if(data === 'Null') {
            return
          }
          //console.log('answer getDataImg', data);
          let type = data.series[0].type;
          this.imgType = type;
          if( type === 'image' || type === 'RGB') this.imgData = data.series;
          else this.imgData = data;

          // if(view.length) {
          //   this.$set(this.chartData, view, data)
          // }
          // else this.chartData = data;
        })
        .catch((err)=> {
          console.log('answer err');
          console.error(err);
        });
    }
  }
};

export default netElementSettingsData


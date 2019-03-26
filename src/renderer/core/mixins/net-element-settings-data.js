import coreRequest  from "@/core/apiCore.js";

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
    }
  },
  computed: {
    currentNetworkID() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkID
    },
    inputPath() {
      return this.settings.accessProperties.Path.join(', ')
    }
  },
  methods: {
    coreRequest,
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
      this.coreRequest(theData)
        .then((data)=> {
          console.log('answer getDataImg', data);
          if(data === 'Null') {
            return
          }
          this.imgData = data;
        })
        .catch((err)=> {
          console.log('answer err');
          console.error(err);
        });
    }
  }
};

export default netElementSettingsData
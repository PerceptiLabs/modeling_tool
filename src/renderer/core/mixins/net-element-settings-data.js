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
      coreRequest(theData)
        .then((data)=> {
          //console.log('answer getDataImg', data);
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
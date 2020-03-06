<template lang="pug">

  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup_tab-set
        .popup_header
            h3 {{ popupTitle }}
      .popup_body
        file-picker(:stylingOptions="stylingOptions")
        
</template>

<script>
import BaseGlobalPopup  from '@/components/global-popups/base-global-popup';
import { pathSlash }  from '@/core/constants.js';
import FilePicker from '@/components/different/file-picker.vue';

export default {
  name: "FilePickerPopup",
  components: { BaseGlobalPopup, FilePicker },
//   props: {
//     popupSettings: {type: Object},
//   },
  data() {
    return {
        popupTitle: 'Export to',
        settings: {
            projectName: '',
            projectPath: '',
            isSaveTrainedModel: true,
        },
        stylingOptions: {
            showBackButton: false,
            showNumberSelectedFiles: false
        }
    }
  },
  methods: {
    closePopup() {
        this.$store.commit('globalView/HIDE_allGlobalPopups');
    },
    answerPopup() {
    //   if(!this.popupSettings.isFreezeInfo) {
    //     this.settings.projectPath = this.settings.projectPath + pathSlash + this.settings.projectName;
    //   }
    //   this.promiseOk(this.settings);
    },
    // loadPathProject() {
    //   if(this.settings.projectPath.length) return;
    //   let opt = {
    //     title:"The folder in which the project will be saved",
    //     properties: ['openDirectory'],
    //   };
    //   openLoadDialog(opt)
    //     .then((pathArr)=> { this.settings.projectPath = pathArr[0] })
    //     .catch(()=> {})
    // },
    
  }
}
</script>

<style lang="scss" scoped>
base-global-popup {
    /deep/ .popup-global .popup_foot {
        display: none;
    }
}
</style>

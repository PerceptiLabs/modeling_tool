<template lang="pug">
  div
    .settings-layer_section
      // .form_row(v-tooltip-interactive:right="interactiveInfo.selected_layer")
      //   .form_label Selected Layer:
      //   #tutorial_selected_layer.form_input(data-tutorial-hover-info)
      //     base-select(
      //       v-model="settings.selected_layer"
      //       :select-options="inputLayers"
      //     )

    //- template(slot="Code-content")
    //-   settings-code(
    //-     :current-el="currentEl"
    //-     :el-settings="settings"
    //-     v-model="coreCode"
    //-   )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'SetMathSwitch',
  mixins: [mixinSet],
  beforeMount() {
    this.inputId.forEach((id)=> {
      let elList = this.currentNetworkList;
      this.inputLayers.push({
        text: elList[id].layerName,
        value: elList[id].layerName,
        tutorialId: elList[id].tutorialId
      })
    });
    if(!this.settings.selected_layer && this.inputLayers.length) this.settings.selected_layer = this.inputLayers[0].value.toString();
  },
  computed: {
    ...mapGetters({
      currentNetworkList: 'mod_workspace/GET_currentNetworkElementList'
    }),
    inputId() {
      return this.currentEl.connectionIn
    }
  },
  data() {
    return {
      inputLayers: [],
      settings: {        
        selected_layer: ''
      },
      interactiveInfo: {
        selected_layer: {
          title: 'Selected Layer',
          text: 'Choose which input connection is represent the selected layer'
        },
      }
    }
  },
  mounted() {
    this.saveSettingsToStore("Settings");
  },
}
</script>

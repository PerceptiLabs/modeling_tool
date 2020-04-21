<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.labels")
          .form_label Labels:
          #tutorial_labels.form_input(data-tutorial-hover-info)
            base-select(
              v-model="settings.Labels"
              :select-options="inputLayers"
            )

    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        :el-settings="settings"
        v-model="coreCode"
      )

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
        value: elList[id].layerId,
        tutorialId: elList[id].tutorialId
      })
    });
    if(!this.settings.Labels && this.inputLayers.length) this.settings.Labels = this.inputLayers[0].value.toString();
  },
  computed: {
    ...mapGetters({
      currentNetworkList: 'mod_workspace/GET_currentNetworkElementList'
    }),
    inputId() {
      console.log(this.currentEl.connectionIn);
      return this.currentEl.connectionIn
    }
  },
  data() {
    return {
      inputLayers: [],
      settings: {        
        Labels: '',
        Dim: -1,
      },
      interactiveInfo: {
        labels: {
          title: 'Labels',
          text: 'Choose which input connection is represent the labels'
        },
      }
    }
  }
}
</script>

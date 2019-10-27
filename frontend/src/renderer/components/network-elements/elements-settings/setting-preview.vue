<template lang="pug">
  .settings-layer_section
    .settings-layer
      .form_row
        button.btn.btn--link(type="button" @click="toSettings")
          i.icon.icon-backward
          span Back
      .form_row
        base-select(
          v-model="previewValue"
          :select-options="previewList"
        )
      .form_row
        chart-switch.data-settings_chart(
          :disable-header="true"
          :chart-data="imgData"
        )
    .settings-layer_foot
      button.btn.btn--primary.btn--disabled(type="button"
        @click="hideAllWindow"
        ) Cancel
      button#tutorial_button-confirm.btn.btn--primary(type="button"
        @click="confirmSettings"
      ) Confirm

</template>

<script>
  //import codeHq    from "@/components/network-elements/elements-settings/code-hq.vue";
  import ChartSwitch  from "@/components/charts/chart-switch.vue";
  import {mapActions} from 'vuex';
export default {
  name: "SettingsPreview",
  inject: ['hideAllWindow'],
  components: {ChartSwitch},
  props: {
    currentEl: { type: Object },
  },
  mounted () {
    this.api_getOutputDim()
      .then((data)=> {
        if(this.currentEl.layerCodeError) this.toSettings();
        else {
          this.getVariableList()
        }
      })

  },
  data() {
    return {
      previewValue: '',
      previewList: [],
      imgData: null,
    }
  },
  computed: {
    layerId() {
      return this.currentEl.layerId
    }
  },
  watch: {
    previewValue(newVal) {
      this.getSample(newVal)
    },
  },
  methods: {
    ...mapActions({
      api_getVariableList:  'mod_api/API_getPreviewVariableList',
      api_getPreviewSample: 'mod_api/API_getPreviewSample',
      api_getOutputDim:     'mod_api/API_getOutputDim',
      tutorialPointActivate:'mod_tutorials/pointActivate',
    }),
    toSettings() {
      this.$emit('to-settings');
    },
    confirmSettings() {
      this.tutorialPointActivate({way: 'next', validation: 'tutorial_button-confirm'});
      this.hideAllWindow();
    },
    getSample(data) {
      this.api_getPreviewSample({layerId: this.layerId, varData: data})
        .then((data)=> {
          this.imgData = data;
        })
    },
    getVariableList() {
      this.api_getVariableList(this.layerId)
        .then((data)=> {
          this.previewValue = data.VariableName;
          this.previewList = data.VariableList;
        })
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "../../../scss/base";
  .settings-layer_foot {
    justify-content: flex-end;
    .btn {
      height: auto;
      min-width: 7rem;
    }
    .btn + .btn {
      margin-left: .8rem;
    }
  }
</style>

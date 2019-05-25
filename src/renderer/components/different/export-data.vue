<template lang="pug">
  .export-data
    base-switcher.export-data_body
      template(slot="firstTab")
        .form_holder
          .form_label Path:
          .form_row
            input.form_input(type="text" v-model="settings.Location" readonly)
            button.btn.btn--dark-blue-rev(type="button" @click="saveLoadFile") Browse
        .form_holder
          .form_label Export as:
          .form_row
            base-select(
              v-model="settings.Type"
              :select-options="selectOptions"
              )
        .form_holder
          base-checkbox(v-model="settings.Compressed") Compressed

      template(slot="secondTab")
        p secondTab
    .export-data_action
      button.btn.btn--primary(type="button" @click="exportData") Export

</template>

<script>
import BaseSwitcher     from "@/components/different/switcher.vue";
import {loadPathFolder} from '@/core/helpers.js'


export default {
  name: "ExportData",
  components: {BaseSwitcher},
  data() {
    return {
      disabledBtn: false,
      selectOptions: [
        { text: 'TensorFlow Model',  value: 'TFModel' },
        { text: 'Docker Image',       value: 'Docker' },
        { text: 'Raw Parameters',     value: 'Raw' }
      ],
      settings: {
        Location: '',
        Type: 'TFModel',
        Compressed: true
      }
    }
  },
  methods: {
    loadPathFolder,
    saveLoadFile() {
      this.disabledBtn = true;
      this.loadPathFolder()
        .then((pathArr)=>{
          this.disabledBtn = false;
          this.settings.Location = pathArr[0];
        })
        .catch((err)=> {
          this.disabledBtn = false;
          console.error(err)
        } )
    },
    exportData() {
      this.$store.dispatch('mod_api/API_exportData', this.settings)
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .export-data_body {
    padding: 2.5rem 2.2rem 0;
    border-bottom: 1px solid $bg-toolbar;
    font-size: 1.2rem;
  }
  .export-data_action {
    text-align: right;
    padding: 1.5rem 2.2rem 0;
  }
</style>

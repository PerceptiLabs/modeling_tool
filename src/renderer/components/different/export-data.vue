<template lang="pug">
  .export-data
    base-switcher.sidebar_section
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
        .sidebar_line
        .form_holder
          base-checkbox(v-model="settings.git")
            i.icon.icon-git
            span.checkbox-info  Git
        .form_holder
          .form_row
            input.form_input(
              type="text"
              placeholder="insert link"
              v-model="settings.gitLink"
              :disabled="!settings.git"
            )
            span &nbsp;&nbsp;or&nbsp;&nbsp;
            button.btn.btn--dark-blue-rev(type="button") Create
      template(slot="secondTab")
        p secondTab
    .sidebar_action
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
        Compressed: false
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
  .export-data {
    font-size: 1.2rem;
  }
</style>

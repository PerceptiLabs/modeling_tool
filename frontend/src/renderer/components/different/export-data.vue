<template lang="pug">
  .export-data
    base-accordion(:accordion-title="accordionData")
      template(slot="exportAs")
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

        .form_holder.text-center
          button.btn.btn--outline-blue.export-button(type="button"
            @click="exportData"
          )
            span Export

      //template(slot="git")
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
              //:disabled="!settings.git"
            )
            span &nbsp;&nbsp;or&nbsp;&nbsp;
            button.btn.btn--dark-blue-rev(type="button") Create

</template>

<script>
import BaseSwitcher     from "@/components/different/switcher.vue";
import {loadPathFolder} from '@/core/helpers.js'
import BaseAccordion    from "@/components/base/accordion.vue";


export default {
  name: "ExportData",
  components: {BaseSwitcher, BaseAccordion},
  data() {
    return {
      accordionData: [
        {name: 'exportAs' , html: 'Export as'},
        //{name: 'git' , html: '<i class="icon icon-git"></i> Git'},
      ],
      selectOptions: [
        { text: 'TensorFlow Model',  value: 'TFModel' },
        //{ text: 'Docker Image',       value: 'Docker' },
        //{ text: 'Raw Parameters',     value: 'Raw' }
      ],
      settings: {
        Location: '',
        Type: 'TFModel',
        Compressed: false
      }
    }
  },
  methods: {
    saveLoadFile() {
      loadPathFolder()
        .then((pathArr)=> this.settings.Location = pathArr[0] )
        .catch((err)=> console.error(err) )
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
  .export-button {
    width: 18rem;
  }
</style>

<template lang="pug">
  .import-data
    base-switcher.sidebar_section
      template(slot="firstTab")
        .form_holder
          .form_label Browse:
          .form_row
            input.form_input(type="text" v-model="settings.Location" readonly)
            button.btn.btn--dark-blue-rev(type="button" @click="saveLoadFile") Search

      template(slot="secondTab")
        p secondTab
    .sidebar_section
      .form_holder
        .form_label Built-in Templates:
        .form_row
          base-select(
            v-model="settings.Type"
            :select-options="selectOptions"
            select-placeholder="placeholder text"
          )
    .sidebar_section
      //-.form_holder
        .form_row
          base-checkbox(v-model="settings.git")
            i.icon.icon-git
            span.checkbox-info Git
      .form_holder
        .form_label Git:
        .form_row
          input.form_input(
            type="text"
            placeholder="insert link"
            v-model="settings.gitLink"
            :disabled="!settings.git"
          )
    .sidebar_action
      button.btn.btn--primary(type="button" @click="importData") Import

</template>

<script>
import BaseSwitcher     from "@/components/different/switcher.vue";
import {loadPathFolder} from '@/core/helpers.js'


export default {
  name: "ImportData",
  components: {BaseSwitcher},
  data() {
    return {
      disabledBtn: false,
      selectOptions: [
        { text: 'Machine Translation',    value: 'machine_translation' },
        { text: 'Image Processing11',       value: null,
          sublist: [
            { text: 'Image Processing 11', value: 'processsing11' },
            { text: 'Image Processing 12', value: 'processdfsing12' },
            { text: 'Image Processing 13', value: 'procesasdsing13' },
            { text: 'Image Processing 14', value: 'processasdasding14' },
          ],
        },
        { text: 'Image Processing',       value: null,
          sublist: [
            { text: 'Image Processing 1', value: 'processing1' },
            { text: 'Image Processing 2', value: 'processing2' },
            { text: 'Image Processing 3', value: 'processing3' },
            { text: 'Image Processing 4', value: 'processing4' },
          ],
        },
        { text: 'Anomalie Detection',     value: 'Anomalie' },
        { text: 'Reinforcement Learning', value: 'Reinforcement' },
        { text: 'NLP',                    value: 'NLP' },
        { text: 'Generative Network',     value: 'Generative' }
      ],
      settings: {
        Location: '',
        Type: 'Anomalie',
        git: false,
        gitLink: ''
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
    importData() {
      this.$store.dispatch('mod_api/API_exportData', this.settings)
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .import-data {
    font-size: 1.2rem;
  }
</style>

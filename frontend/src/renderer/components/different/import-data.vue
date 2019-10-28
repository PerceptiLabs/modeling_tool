<template lang="pug">
  base-accordion(:accordion-title="accordionData")
    template(slot="tensorFlow")
      .tf-wrap.text-center
        button.btn.btn--outline-blue(type="button"
          :disabled="disabledBtn"
          @click="loadTFFiles"
          ) Open

    template(slot="builtIn")
      .form_row.middle-text
        base-select.form_input(
          v-model="settings.Type"
          :select-options="selectOptions"
          select-placeholder="placeholder text"
        )
        button.btn.btn--dark-blue-rev(type="button"
          :disabled="disabledBtn"
          @click="clickQ"
          ) Load

    //template(slot="git")
      .form_row
        input.form_input(type="text" v-model="settings.Location" placeholder="insert link")
        button.btn.btn--dark-blue-rev(type="button"
          //:disabled="disabledBtn"
          @click="clickQ"
          ) Load

</template>

<script>
import BaseSwitcher     from "@/components/different/switcher.vue";
import BaseAccordion    from "@/components/base/accordion.vue";

export default {
  name: "ImportData",
  components: {BaseSwitcher, BaseAccordion},
  data() {
    return {
      disabledBtn: false,
      accordionData: [
        {name: 'tensorFlow' , html: 'TensorFlow Model'},
        {name: 'builtIn' , html: 'Built-in Templates'},
        //{name: 'git' , html: '<i class="icon icon-git"></i> Git'},
      ],
      selectOptions: [
        { text: 'Image Classification',   value: 'ImageClassification' },
        { text: 'Timeseries Regression',  value: 'Timeseries' },
        { text: 'Reinforcement Learning', value: 'Reinforcement' },
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
    loadTFFiles() {
      this.$store.commit('globalView/GP_showWorkspaceBeforeImport', true);
    },
    clickQ() {

    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .tf-wrap {
    .btn {
      min-width: 15rem;
    }
  }
</style>

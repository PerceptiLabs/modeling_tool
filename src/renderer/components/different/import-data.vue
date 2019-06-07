<template lang="pug">
  base-accordion(:accordion-title="accordionData")
    template(slot="tensorFlow")
      .tf-wrap
        button.btn.btn--outline-blue(type="button" @click="clickQ") Open

    template(slot="builtIn")
      .form_row
        base-select.form_input(
          v-model="settings.Type"
          :select-options="selectOptions"
          select-placeholder="placeholder text"
        )
        button.btn.btn--dark-blue-rev(type="button" @click="clickQ") Load

    template(slot="git")
      .form_row
        input.form_input(type="text" v-model="settings.Location" placeholder="insert link")
        button.btn.btn--dark-blue-rev(type="button" @click="clickQ") Load

</template>

<script>
import BaseSwitcher     from "@/components/different/switcher.vue";
import BaseAccordion    from "@/components/base/accordion.vue";
import {loadPathFolder} from '@/core/helpers.js'


export default {
  name: "ImportData",
  components: {BaseSwitcher, BaseAccordion},
  data() {
    return {
      accordionData: [
        {name: 'tensorFlow' , html: 'TensorFlow Model'},
        {name: 'builtIn' , html: 'Built-in Templates'},
        {name: 'git' , html: '<i class="icon icon-git"></i> Git'},
      ],
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
    clickQ() {

    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .tf-wrap {
    text-align: center;
    .btn {
      min-width: 15rem;
    }
  }
</style>

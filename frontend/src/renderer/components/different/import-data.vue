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
          v-model="basicTemplate.currentName"
          :select-options="basicTemplate.templatesList"
          select-placeholder="placeholder text"
        )
        button.btn.btn--dark-blue-rev(type="button"
          :disabled="disabledBtn"
          @click="loadBasicTemplate"
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
import cloneDeep from 'lodash.clonedeep';

import { googleAnalytics } from '@/core/analytics';

import BaseSwitcher     from "@/components/different/switcher.vue";
import BaseAccordion    from "@/components/base/accordion.vue";
import imageClassification    from '@/core/basic-template/image-classification.js'
import reinforcementLearning  from '@/core/basic-template/reinforcement-learning.js'
import timeseriesRegression   from '@/core/basic-template/timeseries-regression.js'
import ganTemplate            from '@/core/basic-template/gan-template.js'

export default {
  name: "ImportData",
  components: {BaseSwitcher, BaseAccordion},
  data() {
    return {
      disabledBtn: false,
      settings: {
        Location: '',
        git: false,
        gitLink: ''
      },
      accordionData: [
        {name: 'tensorFlow' , html: 'TensorFlow Model'},
        {name: 'builtIn' , html: 'Built-in Templates'},
        //{name: 'git' , html: '<i class="icon icon-git"></i> Git'},
      ],
      basicTemplate: {
        currentName: 'imageClassification',
        currentNet: null,
        templatesList: [
          {
            text: 'Image Classification',
            imgPath: './static/img/project-page/image-classification.svg',
            value: 'imageClassification',
            template: imageClassification
          },
          {
            text: 'Timeseries Regression',
            imgPath: './static/img/project-page/time-series-regression.svg',
            value: 'timeseriesRegression',
            template: timeseriesRegression
          },
          {
            text: 'Reinforcement Learning',
            imgPath: './static/img/project-page/reinforcement-learning.svg',
            value: 'reinforcementLearning',
            template: reinforcementLearning
          },
          {
            text: 'GAN Template',
            imgPath: './static/img/project-page/reinforcement-learning.svg',
            value: 'ganTemplate',
            template: ganTemplate
          }
        ],
      }
    }
  },
  watch: {
    'basicTemplate.currentName': {
      handler(newName) {
        const currentIndex = this.basicTemplate.templatesList.findIndex((el)=> el.value === newName);
        this.basicTemplate.currentNet = this.basicTemplate.templatesList[currentIndex].template
      },
      immediate: true
    }
  },
  methods: {
    loadTFFiles() {
      googleAnalytics.trackCustomEvent('export-data');
      this.$store.commit('globalView/GP_showWorkspaceBeforeImport', true);
    },
    loadBasicTemplate() {
      this.$store.dispatch('mod_workspace/ADD_network', cloneDeep(this.basicTemplate.currentNet.network));
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

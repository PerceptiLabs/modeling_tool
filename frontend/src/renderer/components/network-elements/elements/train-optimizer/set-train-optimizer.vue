<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.optimizer")
          .form_label Optimizer:
          .form_input
            base-radio(group-name="group1" value-input="ADAM" v-model="settings.Optimizer")
              span ADAM
            base-radio(group-name="group1" value-input="SGD" v-model="settings.Optimizer")
              span SGD
            base-radio(group-name="group1" value-input="Momentum" v-model="settings.Optimizer")
              span Momentum
            base-radio(group-name="group1" value-input="RMSprop" v-model="settings.Optimizer")
              span RMSprop

        template(v-if="settings.Optimizer === 'ADAM'")
          .form_row
            .form_label Beta 1:
            .form_input
              input(type="number" v-model="settings.Beta_1")
          .form_row
            .form_label Beta 2:
            .form_input
              input(type="number" v-model="settings.Beta_2")
        template(v-if="settings.Optimizer === 'Momentum'")
          .form_row
            .form_label Momentum:
            .form_input
              input(type="number" v-model="settings.Momentum")
          .form_row
            .form_label Decay:
            .form_input
              input(type="number" v-model="settings.Decay")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.learningRate")
          .form_label Learning rate:
          #tutorial_learning_rate.form_input(data-tutorial-hover-info)
            input(type="number" v-model="settings.Learning_rate")

    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        :el-settings="settings"
        v-model="coreCode"
      )

</template>

<script>
import mixinSet from '@/core/mixins/net-element-settings.js';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'SetTrainOptimizer',
  mixins: [ mixinSet ],
  beforeMount() {
    // this.inputId.forEach((id)=> {
    //   let elList = this.currentNetworkList;
    //   this.inputLayers.push({
    //     text: elList[id].layerName,
    //     value: elList[id].layerId,
    //     tutorialId: elList[id].tutorialId
    //   })
    // });
    // if(!this.settings.Labels && this.inputLayers.length) this.settings.Labels = this.inputLayers[0].value.toString();
  },
  data() {
    return {
      inputLayers: [],
      settings: {
        // Labels: '',
        // N_class: '1',
        // Loss: "Cross_entropy", //#Cross_entropy, Quadratic, W_cross_entropy, Dice
        // Class_weights: 1,
        Learning_rate: "0.001",
        Optimizer: "SGD", //#SGD, Momentum, ADAM, RMSprop
        Beta_1: '0.1',
        Beta_2: '0.1',
        Momentum: '0.1',
        Decay: '0.1',
        //Training_iters: "20000"
      },
      interactiveInfo: {
        optimizer: {
          title: 'Optimizer',
          text: 'Choose which optimizer to use'
        },
        learningRate: {
          title: 'Learning rate',
          text: 'Set the learning rate'
        }
      }
    }
  },
  computed: {
    // ...mapGetters({
    //   isTutorialMode:     'mod_tutorials/getIstutorialMode',
    //   currentNetworkList: 'mod_workspace/GET_currentNetworkElementList'
    // }),
    // inputId() {
    //   return this.currentEl.connectionIn
    // },
    // notLabelsInput() {
    //   return this.inputId.filter((id)=>id !== this.settings.Labels)
    // },
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
      popupInfo:               'globalView/GP_infoPopup'
    }),
    saveSettings(tabName) {
      this.applySettings(tabName);
      //this.tutorialPointActivate({way:'next', validation: 'tutorial_cost-function'})
    },
  },
  watch: {
    // 'settings.Labels': {
    //   handler(newValue) {
    //     let label = this.inputLayers.filter((item)=> {
    //       return item.value.toString() === newValue;
    //     });
    //     if(this.isTutorialMode && label[0].text !== 'OneHot_1') {
    //       label = this.inputLayers.filter((item)=> {
    //         return item.text === 'OneHot_1';
    //       });
    //         this.settings.Labels = label[0].value.toString();
    //         this.popupInfo("Please set One Hot for Labels field when you in tutorial mode");
    //     }
    //   }
    // },
  }
}
</script>

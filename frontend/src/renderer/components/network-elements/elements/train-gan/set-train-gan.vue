<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Settings-content")
      // .settings-layer_section
      //   .form_row(v-tooltip-interactive:right="interactiveInfo.labels")
      //     .form_label Labels:
      //     #tutorial_labels.form_input(data-tutorial-hover-info)
      //       base-select(
      //         v-model="settings.Labels"
      //         :select-options="inputLayers"
      //       )
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.labels")
          .form_label Switch:
          #tutorial_labels.form_input(data-tutorial-hover-info)
            base-select(
              v-model="settings.switch_layer"
              :select-options="allSwitchLayers"
            )
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.labels")
          .form_label Real Data:
          #tutorial_labels.form_input(data-tutorial-hover-info)
            base-select(
              v-model="settings.real_data_layer"
              :select-options="allRealDataLayers"
            )
      .settings-layer_section
        .form_row
          .form_label Epochs:
          .form_input
            input(type="number" v-model="settings.Epochs")
      // .settings-layer_section
      //   .form_row(v-tooltip-interactive:right="interactiveInfo.costFunction")
      //     .form_label Cost function:
      //     #tutorial_cost-function.tutorial-relative.form_input(data-tutorial-hover-info)
      //       base-radio(group-name="group" value-input="Cross_entropy" v-model="settings.Loss")
      //         span Cross-Entropy
      //       base-radio(group-name="group" value-input="Quadratic" v-model="settings.Loss")
      //         span Quadratic
      //       base-radio(group-name="group" value-input="W_cross_entropy" v-model="settings.Loss")
      //         span Weighted Cross-Entropy
      //       base-radio(group-name="group" value-input="Dice" v-model="settings.Loss")
      //         span DICE
      //       base-radio(group-name="group" value-input="Regression" v-model="settings.Loss")
      //         span Regression
      //         //-Cross-Entropy
      //   .form_row(v-if="settings.Loss === 'W_cross_entropy'")
      //     .form_label Class weights:
      //     .form_input
      //       input(type="number" v-model="settings.Class_weights")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.optimizer")
          .form_label Optimizer:
          #tutorial_optimizer.form_input(data-tutorial-hover-info)
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
            .form_label Decay rate:
            .form_input
              input(type="number" v-model="settings.Decay_rate")
          .form_row
            .form_label Decay steps:
            .form_input
              input(type="number" v-model="settings.Decay_steps")
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
  name: 'SetTrainGan',
  mixins: [ mixinSet ],
  beforeMount() {
    let elList = this.currentNetworkList;
    this.inputId.forEach((id)=> {
      this.inputLayers.push({
        text: elList[id].layerName,
        value: elList[id].layerId,
        tutorialId: elList[id].tutorialId
      })
    });
    for(let key in elList) {
      if(elList[key].layerType==="Data") {
        this.allRealDataLayers.push({
          text: elList[key].layerName,
          value: elList[key].layerId,
          tutorialId: elList[key].tutorialId
        })
      }
      if(elList[key].layerType==="Other") {
        this.allSwitchLayers.push({
          text: elList[key].layerName,
          value: elList[key].layerId,
          tutorialId: elList[key].tutorialId
        })
      }
    }
    if(!this.settings.Labels && this.inputLayers.length) this.settings.Labels = this.inputLayers[0].value.toString();
    if(!this.settings.switch_layer && this.allSwitchLayers.length) this.settings.switch_layer = this.allSwitchLayers[0].value.toString();
    if(!this.settings.real_data_layer && this.allRealDataLayers.length) this.settings.real_data_layer = this.allRealDataLayers[0].value.toString();
  },
  data() {
    return {
      inputLayers: [],
      allSwitchLayers: [],
      allRealDataLayers: [],
      settings: {
        Labels: '',
        switch_layer: '',
        real_data_layer: '',
        Epochs: '10',
        N_class: '1',
        Loss: "Quadratic", //#Cross_entropy, Quadratic, W_cross_entropy, Dice
        Class_weights: '1',
        Learning_rate: "0.001",
        Optimizer: "ADAM", //#SGD, Momentum, ADAM, RMSprop
        Beta_1: '0.9',
        Beta_2: '0.999',
        Momentum: '0.9',
        Decay_steps: '100000',
        Decay_rate: '0.96',
        Training_iters: "20000"
      },
      interactiveInfo: {
        labels: {
          title: 'Labels',
          text: 'Choose which input connection is represent the labels'
        },
        // costFunction: {
        //   title: 'Split on',
        //   text: 'Choose in which position to split on at the chosen axis'
        // },
        // optimizer: {
        //   title: 'Optimizer',
        //   text: 'Choose which optimizer to use'
        // },
        learningRate: {
          title: 'Learning rate',
          text: 'Set the learning rate'
        }
      }
    }
  },
  computed: {
    ...mapGetters({
      isTutorialMode:     'mod_tutorials/getIstutorialMode',
      currentNetworkList: 'mod_workspace/GET_currentNetworkElementList'
    }),
    inputId() {
      return this.currentEl.connectionIn
    },
    notLabelsInput() {
      return this.inputId.filter((id)=>id !== this.settings.Labels)
    },
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
      popupInfo:               'globalView/GP_infoPopup'
    }),
    saveSettings(tabName) {
      this.applySettings(tabName);
      this.$nextTick(()=> this.tutorialPointActivate({way: 'next', validation: 'tutorial_labels'}));
    },
  },
  watch: {
    'settings.Labels': {
      handler(newValue) {
        let label = this.inputLayers.filter((item)=> {
          return item.value.toString() === newValue;
        });
        if(this.isTutorialMode && label[0].text !== 'OneHot_1') {
          label = this.inputLayers.filter((item)=> {
            return item.text === 'OneHot_1';
          });
            this.settings.Labels = label[0].value.toString();
            this.popupInfo("Please set One Hot for Labels field when you in tutorial mode");
        }
      }
    },
  }
}
</script>

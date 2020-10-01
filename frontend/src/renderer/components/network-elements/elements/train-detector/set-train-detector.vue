<template lang="pug">
  div
    .settings-layer_section
      .form_row
        .form_label(v-tooltip-interactive:right="interactiveInfo.epochs") Epochs:
        #tutorial_epochs.form_input(data-tutorial-hover-info)
          input(
            type="number" 
            v-model="settings.Epochs"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row
        .form_label(v-tooltip-interactive:right="interactiveInfo.grid_size") Grid Size:
        #tutorial_grid_size.form_input(data-tutorial-hover-info)
          input(
            type="number"
            v-model="settings.grid_size"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row
        .form_label(v-tooltip-interactive:right="interactiveInfo.batch_size") Batch Size:
        #tutorial_batch_size.form_input(data-tutorial-hover-info)
          input(
            type="number"
            v-model="settings.batch_size"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row
        .form_label(v-tooltip-interactive:right="interactiveInfo.num_box") Number of Boxes:
        #tutorial_num_box.form_input(data-tutorial-hover-info)
          input(
            type="number"
            v-model="settings.num_box"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row
        .form_label(v-tooltip-interactive:right="interactiveInfo.threshold") Threshold:
        #tutorial_threshold.form_input(data-tutorial-hover-info)
          input(
            type="number"
            v-model="settings.threshold"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row
        .form_label(v-tooltip-interactive:right="interactiveInfo.lambda_class") λ
          sub classification:
        #tutorial_lambda_class.form_input(data-tutorial-hover-info)
          input(type="number" v-model="settings.lambda_class")
    .settings-layer_section
      .form_row
        .form_label(v-tooltip-interactive:right="interactiveInfo.lambda_noobj") λ
          sub non object:
        #tutorial_lambda_noobj.form_input(data-tutorial-hover-info)
          input(type="number" v-model="settings.lambda_noobj")
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
            input(
              type="number"
              v-model="settings.Beta_1"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
        .form_row
          .form_label Beta 2:
          .form_input
            input(
              type="number"
              v-model="settings.Beta_2"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
      template(v-if="settings.Optimizer === 'Momentum'")
        .form_row
          .form_label Momentum:
          .form_input
            input(
              type="number"
              v-model="settings.Momentum"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
        .form_row
          .form_label(v-tooltip-interactive:right="interactiveInfo.lambda_class") λ
            sub classification:
          #tutorial_lambda_class.form_input(data-tutorial-hover-info)
            input(
              type="number"
              v-model="settings.lambda_class"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
      .settings-layer_section
        .form_row
          .form_label(v-tooltip-interactive:right="interactiveInfo.lambda_noobj") λ
            sub non object:
          #tutorial_lambda_noobj.form_input(data-tutorial-hover-info)
            input(
              type="number"
              v-model="settings.lambda_noobj"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
 
        .form_row
          .form_label Decay rate:
          .form_input
            input(
              type="number"
              v-model="settings.Decay_rate"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
        .form_row
          .form_label Decay steps:
          .form_input
            input(
              type="number"
              v-model="settings.Decay_steps"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.learningRate")
        .form_label Learning rate:
        #tutorial_learning_rate.form_input(data-tutorial-hover-info)
          input(
            type="number"
            v-model="settings.Learning_rate"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
    .settings-layer_section
      .form_row
        .form_label Additional Stop Condition:
        #tutorial_stop-condition.tutorial-relative.form_input(data-tutorial-hover-info)
          base-radio(group-name="group2" value-input="Epochs" v-model="settings.Stop_condition")
            span None
          base-radio(group-name="group2" value-input="TargetAccuracy" v-model="settings.Stop_condition")
            span Target Accuracy
      template(v-if="settings.Stop_condition === 'TargetAccuracy'")
        .form_row
          .form_label Target Accuracy for Stop Condition:
          .form_input
            input(
              type="number"
              v-model="settings.Stop_Target_Accuracy"
              @focus="setIsSettingInputFocused(true)"
              @blur="setIsSettingInputFocused(false)") 
            span %

    //- template(slot="Code-content")
    //-   settings-code(
    //-     :current-el="currentEl"
    //-     :el-settings="settings"
    //-     v-model="coreCode"
    //-   )

</template>

<script>
import mixinSet from '@/core/mixins/net-element-settings.js';
import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'SetTrainDetector',
  mixins: [ mixinSet, mixinFocus ],
  beforeMount() {
    this.inputId.forEach((id)=> {
      let elList = this.currentNetworkList;
      this.inputLayers.push({
        text: elList[id].layerName,
        value: elList[id].layerId,
        tutorialId: elList[id].tutorialId
      })
    });
    if(!this.settings.Labels && this.inputLayers.length) this.settings.Labels = this.inputLayers[0].value.toString();
  },
  data() {
    return {
      inputLayers: [],
      settings: {
        Labels: '',
        Epochs: '10',
        grid_size: '7',
        batch_size: '3',
        num_box: '2',
        threshold: '0.8',
        lambda_class: '0.5',
        lambda_noobj: '0.1',
        N_class: '1',
        Loss: "Quadratic", //#Cross_entropy, Quadratic, W_cross_entropy, Dice
        Stop_condition: "Epochs",
        Stop_Target_Accuracy: 0,
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
          text: 'Choose which input connection represents the labels'
        },
        epochs: {
          title: 'epochs',
          text: 'Choose'
        },
        grid_size: {
          title: 'Grid Size',
          text: 'Input the grid size'
        },
        batch_size: {
          title: 'Batch Size',
          text: 'Input the batch size'
        },
        num_box: {
          title: 'Number of Box',
          text: 'Input number of box'
        },
        threshold: {
          title: 'Threshold',
          text: 'Input the threshold'
        },
        lambda_class: {
          title: 'Lambda Coord',
          text: 'Input the Lambda Coord'
        },
        lambda_noobj: {
          title: 'Lambda No Obj',
          text: 'Input the Lambda No Obj'
        },
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
  mounted() {
    this.saveSettingsToStore("Settings");
  },
  computed: {
    ...mapGetters({
      isTutorialMode:     'mod_tutorials/getIsTutorialMode',
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
      popupInfo:               'globalView/GP_infoPopup'
    }),
    saveSettings(tabName) {
      this.applySettings(tabName);
    },
  },
}
</script>

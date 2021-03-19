<template lang="pug">
  base-global-popup(
    :tab-set="popupTitle"
    class="global-training-settings"
  )
    template(:slot="popupTitle[0] + '-content'")
      .form_row
        .form_label
          info-tooltip(
            text="Number of times you want to run through the entire dataset. The more number of times, the better the model will learn you training data. Just be aware that training too long may overfit your model to your training data."
          ) Epochs:
        #tutorial_epochs.form_input(data-tutorial-hover-info)
          input.normalize-inputs(
            type="number"
            name="Epochs"
            :value="settings.Epochs"
            @input="handleInputChange"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
      .form_row
        .form_label
          info-tooltip(
            text="Number of samples you want to train on at the same time. Higher value will cause the training to go quicker and may make your model generalize better. Too high value may cause your model not to learn the data well enough though."
          ) Batch size:
        .form_input
          input.normalize-inputs(
            type="number"
            name="Batch_size"
            :value="settings.Batch_size"
            @input="handleInputChange"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
      .form_row
        .form_label
          info-tooltip(
            text="The loss function is how the error between the prediction and the labels is calculated and therefore what the models tries to optimize."
          ) Loss:
        .form_input
          base-select(
            :value="settings.Loss"
            @input="handleCheckboxAndSelectChange($event, 'Loss')"
            :select-options="defaultTrainingSettings.LossOptions"
          )
      .form_row(v-tooltip-interactive:right="interactiveInfo.learningRate")
        .form_label
          info-tooltip(
            text="The higher the value, the quicker your model will learn. If it's too low it can easily get stuck in a poor local minima and it it's too high it can easily skip over good local minimas."
          ) Learning rate:
        #tutorial_learning_rate.form_input
          input.normalize-inputs(
            type="number"
            name="Learning_rate"
            :value="settings.Learning_rate"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)")
      .form_row
        .form_label Optimizer:
        .form_input
          base-select(
            :value="settings.Optimizer"
            @input="handleCheckboxAndSelectChange($event, 'Optimizer')"
            :select-options="defaultTrainingSettings.OptimizerOptions"
          )
          br
          div(v-if="settings.Optimizer === 'ADAM'")
            .form_row
              .form_label
                info-tooltip(
                  text="The exponential decay rate for the 1st moment estimates"
                ) Beta1:
              .form_input(data-tutorial-hover-info)
                input.normalize-inputs(
                  type="number"
                  name="Beta1"
                  :value="settings.Beta1"
                  @input="handleInputChange"
                  @focus="setIsSettingInputFocused(true)"
                  @blur="setIsSettingInputFocused(false)")
            .form_row
              .form_label
                info-tooltip(
                  text="The exponential decay rate for the 2nd moment estimates"
                ) Beta2:
              .form_input(data-tutorial-hover-info)
                input.normalize-inputs(
                  type="number"
                  name="Beta2"
                  :value="settings.Beta2"
                  @input="handleInputChange"
                  @focus="setIsSettingInputFocused(true)"
                  @blur="setIsSettingInputFocused(false)")
          div(v-if="settings.Optimizer === 'SGD'")
            .form_row
              .form_label
                info-tooltip(
                  text="Accelerates the gradient descent in the relevant direction and dampens oscillations"
                ) Momentum:
              .form_input(data-tutorial-hover-info)
                input.normalize-inputs(
                  type="number"
                  name="Momentum"
                  :value="settings.Momentum"
                  @input="handleInputChange"
                  @focus="setIsSettingInputFocused(true)"
                  @blur="setIsSettingInputFocused(false)")
          div(v-if="settings.Optimizer === 'RMSprop'")
            .form_row
              info-tooltip(
                text="Setting this to True may help with training, but is slightly more expensive in terms of computation and memory"
              ) 
                base-checkbox(:value="settings.Centered" @input="handleCheckboxAndSelectChange($event, 'Centered')") Centered
      
      .form_row(v-tooltip-interactive:right="interactiveInfo.learningRate")
        .form_label
        .form_input
          info-tooltip(
            text="Select Yes if you want to re-shuffle the order of your dataset each epoch. Typically helps your model to generalize better."
          )
            base-checkbox(:value="settings.Shuffle" @input="handleCheckboxAndSelectChange($event, 'Shuffle')") Shuffle
    template(slot="action")
      //button.btn.btn--primary.btn--disabled(type="button"  @click="closeModal") Cancel
      button.btn.btn--primary(type="button" @click="run()") Run Model
</template>
<script>
  import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";
  import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
  import { defaultTrainingSettings} from "@/core/constants";
  import { mapState } from 'vuex';
  import InfoTooltip from '@/components/different/info-tooltip.vue';
  
  export default {
    name: 'GlobalTrainingSettings',
    components: { BaseGlobalPopup, InfoTooltip },
    mixins: [ mixinFocus ],
    data() {
      return {
        defaultTrainingSettings,
        popupTitle: ['Model training settings'],
        interactiveInfo: {
          learningRate: '',
        },
      }
    },
    computed: {
     ...mapState({
       isModalOpened: state => state.globalView.globalPopup.showGlobalTrainingSettingsPopup.isOpen,
       modalCb: state => state.globalView.globalPopup.showGlobalTrainingSettingsPopup.cb,
     }),
      settings() {
        return this.$store.getters['mod_workspace/GET_modelTrainingSetting'];
      },
    },
    created() {
      console.log(this.isModalOpened)
      // alert('GlobalTrainingSettings is created')
    },
    methods: {
      closeModal() {
        this.$store.dispatch('globalView/showGlobalTrainingSettingsAction',{isOpen: false, cb: () => null}, { root: true} );
      },
      run() {
        this.modalCb();
        this.closeModal();
      },
      handleInputChange(e) {
        const { name, value } = e.target;
        console.log(name, value);
        this.$store.dispatch('mod_workspace/setModelRunSettingsAction', {name, value}, { root: true});
        
      },
      handleCheckboxAndSelectChange(value, name) {
        this.$store.dispatch('mod_workspace/setModelRunSettingsAction', {name, value}, { root: true});
      }
    }
  }
</script>
<style lang="scss">

  .normalize-inputs {
     width: 100% !important;
    height: 32px !important;
  }
  .global-training-settings {
    .settings-layer_section {
      padding: 25px;
    }
    .popup_foot {
      padding: 0 25px 15px;
    }
  }
</style>
<!--//Epochs: 100,-->
<!--//Batch_size: 128,-->
<!--//Shuffle: true,-->
<!--//Loss: '', //[Cross-Entropy, Quadratic, Weighted Cross-Entropy, Dice]-->
<!--//LossOptions: [-->
<!--//{name: 'Cross-Entropy', value: 'Cross-Entropy'},-->
<!--//{name: 'Quadratic', value: 'Quadratic'},-->
<!--//{name: 'Weighted', value: 'Weighted'},-->
<!--//{name: 'Cross-Entropy', value: 'Cross-Entropy'},-->
<!--//{name: 'Dice', value: 'Dice'},-->
<!--//],-->
<!--//Learning_rate: 0.001,-->
<!--//Optimizer: 'ADAM', // [ADAM,SGD,Adagrad,RMSprop]-->
<!--//OptimizerOptions: [-->
<!--//{name: 'ADAM', value: 'ADAM'},-->
<!--//{name: 'SGD', value: 'SGD'},-->
<!--//{name: 'Adagrad', value: 'Adagrad'},-->
<!--//{name: 'RMSprop', value: 'RMSprop'},-->
<!--//],-->
<!--//Beta1: 0.9,-->
<!--//Beta2: 0.999,-->
<!--//Momentum: 0,-->
<!--//Centered: false,-->
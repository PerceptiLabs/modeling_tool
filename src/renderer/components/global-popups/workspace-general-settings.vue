<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closeGlobalSet()")
    section.popup
      .popup_tab-set
        .popup_header.active
          h3 General Settings
      .popup_body
        .settings-layer_section(v-if="settingsData")
          .form_row
            .form_label Data partition:
            .form_input
              label.form_row
                .form_label Training
                .form_input(id="tutorial_partition-training-input" class="tutorial-relative" data-tutorial-hover-info)
                  input(type="number"
                    v-model="settings.Data_partition.Training"
                    name="Training"
                    ref="trainingInput"
                    v-validate="'between:0.001,100|required'"
                    )
                  span &nbsp; %
                  p.text-error(v-show="errors.has('Training')") {{ errors.first('Training') }}
              label.form_row
                .form_label Validation
                .form_input(id="tutorial_partition-validation-input" class="tutorial-relative" data-tutorial-hover-info)
                  input(type="number"
                    v-model="settings.Data_partition.Validation"
                    name="Validation"
                    v-validate="'between:0.001,100|required'"
                    @focus="onFocus('tutorial_partition-training-input')"
                    )
                  span &nbsp; %
                  p.text-error(v-show="errors.has('Validation')") {{ errors.first('Validation') }}
              label.form_row
                .form_label Test
                .form_input(id="tutorial_partition-test-input" class="tutorial-relative" data-tutorial-hover-info)
                  input(type="number"
                    v-model="settings.Data_partition.Test"
                    name="Test"
                    v-validate="'between:0.001,100|required'"
                    )
                  span &nbsp; %
                  p.text-error(v-show="errors.has('Test')") {{ errors.first('Test') }}
        .settings-layer_section(v-if="settingsEnvironment")
          label.form_row
            .form_label Max Steps:
            .form_input
              input(type="number"
              v-model="settings.MaxSteps"
              name="Max_steps"
              v-validate="'min_value:1'"
              )
              p.text-error(v-show="errors.has('Max_steps')") {{ errors.first('Max_steps') }}
        .settings-layer_section
          label.form_row
            .form_label Batch size:
            .form_input(id="tutorial_butch-size-input" class="tutorial-relative" data-tutorial-hover-info)
              input(type="number"
                v-model="settings.Batch_size"
                name="Batch"
                v-validate="'min_value:1'"
                )
              p.text-error(v-show="errors.has('Batch')") {{ errors.first('Batch') }}
        .settings-layer_section
          .form_row
            .form_label Shuffle data:
            .form_input
              base-radio(group-name="group2" :value-input="true" v-model="settings.Shuffle_data")
                span Yes
              base-radio(group-name="group2" :value-input="false" v-model="settings.Shuffle_data")
                span No
        .settings-layer_section
          label.form_row
            .form_label Epochs:
            .form_input(id="tutorial_epochs-input" class="tutorial-relative" data-tutorial-hover-info)
              input(type="number"
                v-model="settings.Epochs"
                name="Epochs"
                ref="epochsInput"
                v-validate="'min_value:1'"
                )
              p.text-error(v-show="errors.has('Epochs')") {{ errors.first('Epochs') }}
        .settings-layer_section
          .form_row
            .form_label Dropout rate:
            .form_input(id="tutorial_drop-rate-input" class="tutorial-relative" data-tutorial-hover-info)
              input(type="number"
                v-model="settings.Dropout_rate"
                name="Dropout"
                v-validate="'between:0.001,100|required'"
                )
              p.text-error(v-show="errors.has('Dropout')") {{ errors.first('Dropout') }}
        .settings-layer_section
          label.form_row
            .form_label Save model every:
            .form_input
              input(type="number" v-model="settings.Save_model_every" disabled="disabled")
              span &nbsp; epoch
      .popup_foot
        button.btn.btn--primary.tutorial-relative(
          type="button"
          @click="validateForm()"
          id="tutorial_apply-button"
        ) Apply

</template>

<script>
import { mapGetters, mapActions } from 'vuex';
export default {
  name: "GeneralSettings",
  mounted() {
    const net = this.networkElementList;
    const settings = this.networkSettings;
    if(settings !== null) {
      this.settings = JSON.parse(JSON.stringify(settings));
    }

    for(let elID in net) {
      const el = net[elID];
      if(el.componentName === 'DataData') this.settingsData = true;
      if(el.componentName === 'DataEnvironment') this.settingsEnvironment = true;
    }
    if(this.isTutorialMode) this.$nextTick(()=>{this.$refs.trainingInput.focus()})
  },
  data() {
    return {
      settingsData: false,
      settingsEnvironment: false,
      settings: {
        Epochs: "1",
        Batch_size: "32",
        MaxSteps: "1000",
        Data_partition: {
          Training: "70",
          Validation: "20",
          Test: "10"
        },
        Dropout_rate: "0.5",
        Shuffle_data: true,
        Save_model_every: "0"
      }
    }
  },
  computed: {
    ...mapGetters({
      isTutorialMode:     'mod_tutorials/getIstutorialMode',
      networkSettings:    'mod_workspace/GET_currentNetworkSettings',
      networkElementList: 'mod_workspace/GET_currentNetworkElementList',
    }),
    testValue() {
      return 100 - (+this.settings.Data_partition.Training + +this.settings.Data_partition.Validation)
    }
  },
  watch: {
    testValue(newVal) {
      this.settings.Data_partition.Test = newVal.toString()
    }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    validateForm() {
      this.$validator.validateAll()
        .then((result) => {
          if (result) {
            this.setGlobalSet();
            this.tutorialPointActivate({way: 'next', validation:'tutorial_partition-training-input'});
            return;
          }
          //error func
        });
    },
    setGlobalSet() {
      this.$store.dispatch('mod_workspace/SET_networkSettings', this.settings);
      this.closeGlobalSet();
      this.$store.commit('globalView/GP_showCoreSideSettings', true);
    },
    closeGlobalSet() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
    },
    onFocus(inputId) {
      this.tutorialPointActivate({way:'next', validation: inputId})
    },
    onBlur(inputId) {
      this.tutorialPointActivate({way:'next', validation: inputId})
    },
    focusEpochsInput() {
      this.$refs.epochsInput.focus()
    }
  }
}
</script>
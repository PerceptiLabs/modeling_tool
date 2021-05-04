<template lang="pug">
  div
    .settings-layer_section
      .form_row
        .form_label Number of Inputs
        .form_input
          input(
            type="number"
            v-model="settings.InputsCount"
            @focus="setIsSettingInputFocused(true)"
            @blur="setIsSettingInputFocused(false)"
          )
      .form_row(v-tooltip-interactive:right="interactiveInfo.operation")
        .form_label Operation:
        .form_input
          div
            base-radio(group-name="group" value-input="Concat" v-model="settings.Type")
              span Concatenate
            .form_row(v-if="settings.Type === 'Concat' ")
              span Merge dimension
              .form_input
                input(
                  type="number"
                  v-model="settings.Merge_dim"
                  @focus="setIsSettingInputFocused(true)"
                  @blur="setIsSettingInputFocused(false)")
          div
            base-radio(group-name="group" value-input="Sub" v-model="settings.Type")
              span Subtraction
          div
            base-radio(group-name="group" value-input="Add" v-model="settings.Type")
              span Addition
          div
            base-radio(group-name="group" value-input="Multi" v-model="settings.Type")
              span Multiplication
          div
            base-radio(group-name="group" value-input="Div" v-model="settings.Type")
              span Division

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
export default {
  name: 'SetMathSplit',
  mixins: [mixinSet, mixinFocus],
  data() {
    return {
      settings: {
        Type: "Add", //#Add, Sub, Multi, Div, Concat
        Merge_dim: '-1',
        InputsCount: 2,
      },
      interactiveInfo: {
        operation: {
          title: 'Operation',
          text: 'Choose which operation to use'
        }
      }
    }
  },
  computed: {
    getMergeComponentInputs () {
      return this.currentEl.inputs
    },
    getLastEditableInputId(){
      let newInputs = {};
      const componentInputs = this.getMergeComponentInputs;
      Object.keys(componentInputs).map(key => {
        if(!componentInputs[key].isDefault) {
          newInputs[key] = componentInputs[key];
        }
      })
      const newInputsKeys = Object.keys(newInputs);
      const lastInputId = newInputsKeys[newInputsKeys.length - 1]; 
      return lastInputId;
    },
    getMergeComponentInputsCount () {
      return Object.keys(this.getMergeComponentInputs).length;
    },
    layerId () {
      return this.currentEl.layerId;
    }
  },
  mounted() {
    this.settings.InputsCount = this.getMergeComponentInputsCount;
    this.saveSettingsToStore("Settings");
  },
  methods: {
    handleInputNumberChanged(inputCount) {
      let inputsCount =  isNaN(inputCount) ? 2 : inputCount;
      let currentInputsCount =  this.getMergeComponentInputsCount;
      
      let shouldAddInputs = inputsCount > currentInputsCount;
      let difference = Math.abs(inputsCount - currentInputsCount);

      for(let i = 0; i < difference; i++) {
        setTimeout(() => {
          shouldAddInputs ? this.addInput(i + currentInputsCount + 1) : this.removeInput()
        }, 0)
      }
    },
    addInput(inputNr) {
      this.$store.commit('mod_workspace/ADD_inputVariableMutation', {
        layerId: this.layerId,
        name: `input${inputNr}`
      });
    },
    removeInput() {
      const lastInputId = this.getLastEditableInputId;
      this.$store.dispatch('mod_workspace/DELETE_inputVariableAction', {
        layerId: this.layerId,
        inputVariableId: lastInputId,
      });
    }
  },
  watch: {
    'settings.InputsCount': {
      handler(current, previous) {
        const shouldSkip = current === "" && previous !== "";
        if(shouldSkip) {
          return;
        }
        
        const currentValue = parseInt(current, 10);
        const isLessThenMin = currentValue < 2;
        if(isLessThenMin) {
          this.settings.InputsCount = 2;
        }
        if (current >= 2) {
          this.handleInputNumberChanged(this.settings.InputsCount)
        }
      }
    }
  }
}
</script>

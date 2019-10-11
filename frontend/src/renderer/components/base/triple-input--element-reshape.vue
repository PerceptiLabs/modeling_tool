<template lang="pug">
  .triple-input
    .triple-input_input-wrap
      input.triple-input_input(type="number" name="field1" min="0"
        :disabled="disableEdit"
        v-model.number="value1"
        :class="{'bg-error': errors.has('field1') || isNotValidateSum}"
        v-validate="{required: true, between: [validateMin, validateMax]}"
      )
      span.triple-input_input-axios {{axisName[0]}}
    //-p.text-error(
      v-show="errors.has('field1')"
      ) {{ errors.first('field1') }}
    button.triple-input_separate.btn.btn--link(type="button" @click="swap12")
      i.icon.icon-swap-horiz
    .triple-input_input-wrap
      input.triple-input_input(type="number" name="field2" min="0"
        :disabled="disableEdit"
        v-model.number="value2"
        :class="{'bg-error': errors.has('field2') || isNotValidateSum || (value2 > 0 && value1 === 0)}"
        v-validate="{required: true, between: [validateMin, validateMax]}"
      )
      span.triple-input_input-axios {{axisName[1]}}
    button.triple-input_separate.btn.btn--link(type="button" @click="swap23")
      i.icon.icon-swap-horiz
    .triple-input_input-wrap
      input.triple-input_input(type="number" name="field3" min="0"
        :disabled="disableEdit"
        v-model.number="value3"
        :class="{'bg-error': errors.has('field3') || isNotValidateSum || (value3 > 0 && (value2 === 0 || value1 === 0))}"
        v-validate="{required: true, between: [validateMin, validateMax]}"
      )
      span.triple-input_input-axios {{axisName[2]}}
    button.triple-input_separate.btn.btn--link(type="button" @click="swap13")
      i.icon.icon-swap-horiz
</template>

<script>

export default {
  name: "TripleInputElementReshape",
  model: {
    prop: 'inputData',
    event: 'input'
  },

  props: {
    inputData: Array,
    disableEdit: { type: Boolean, default: false },
    validateMin: { type: Number, default: 0 },
    validateMax: { type: Number, default: 10000 },
    validateSum: { type: String, default: '' },
    axisPosition: { type: Array },
  },
  computed: {
    isNotValidateSum() {
      console.log(this.validateSum);
      if(this.value1 === 0) return true;
      if(!!this.validateSum.length) {
        const validate = JSON.parse(this.validateSum)[0];
        const val1 = this.value1 > 0 ? this.value1 : 1;
        const val2 = this.value2 > 0 ? this.value2 : 1;
        const val3 = this.value3 > 0 ? this.value3 : 1;
        return validate !== (val1 * val2 * val3)
      }
      else return false
    },
    value1: {
      get() {
        if(this.inputData) { return this.inputData[0] }
      },
      set(newValue) {
        this.$emit('input', [newValue, this.value2, this.value3])
      }
    },
    value2: {
      get() {
        if(this.inputData) { return this.inputData[1] }
      },
      set(newValue) {
        this.$emit('input', [this.value1, newValue, this.value3])
      }
    },
    value3: {
      get() {
        if(this.inputData) { return this.inputData[2] }
      },
      set(newValue) {
        this.$emit('input', [this.value1, this.value2, newValue])
      }
    },
    axisName() {
      return this.axisPosition.map((el)=> {
        if(el === 0) return 'X';
        else if(el === 1) return 'Y';
        else if(el === 2) return 'Z';
        else  return '?';
      })
    }
  },
  methods: {
    swap12() { this.$emit('swap12') },
    swap23() { this.$emit('swap23') },
    swap13() { this.$emit('swap13') }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  @import "../../scss/components/triple-input";
  .triple-input_input {
    max-width: 2em;
  }
  .triple-input_input-wrap {
    position: relative;
  }
  .triple-input_input-axios {
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    color: $col-primary2;
    font-weight: 700;
    font-size: 1rem;
  }
</style>

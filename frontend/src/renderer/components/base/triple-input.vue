<template lang="pug">
  .triple-input(:class="styleType")
    span.labels.first(v-if="withLabels") Training:
    .triple-input-wrapper
      input.triple-input_input(type="number"
        :disabled="disableEdit"
        v-model.number="value1"
        name="field1"
        :class="{'bg-error': errors.has('field1') || isNotValidateSum}"
        v-validate="{required: true, between: [validateMin, validateMax]}"
        @focus="$emit('handle-focus')"
        @blur="$emit('handle-blur')"
      )
      span.triple-input_separate {{ separateSign || 'X'}}
    .triple-input-wrapper
      span.labels(v-if="withLabels") Validation:
      input.triple-input_input(type="number"
        :disabled="disableEdit"
        v-model.number="value2"
        name="field2"
        :class="{'bg-error': errors.has('field2') || isNotValidateSum}"
        v-validate="{required: true, between: [validateMin, validateMax]}"
        @focus="$emit('handle-focus')"
        @blur="$emit('handle-blur')"
      )
      span.triple-input_separate {{ separateSign || 'X' }}
    .triple-input-wrapper
      span.labels(v-if="withLabels") Test:
      input.triple-input_input(type="number"
        :disabled="disableEdit"
        v-model.number="value3"
        name="field3"
        :class="{'bg-error': errors.has('field3') || isNotValidateSum}"
        v-validate="{required: true, between: [validateMin, validateMax]}"
        @focus="$emit('handle-focus')"
        @blur="$emit('handle-blur')"
      )
      span.triple-input_separate(v-if="separateSign") {{ separateSign }}
</template>

<script>
export default {
  name: "TripleInput",
  model: {
    prop: 'inputData',
    event: 'input'
  },

  props: {
    inputData: Array,
    separateSign: {
      type: String,
      default: ''
    },
    disableEdit: {
      type: Boolean,
      default: false
    },
    validateMin: { type: Number, default: -9999 },
    validateMax: { type: Number, default: 10000 },
    validateSum: { type: Number, default: null },
    withLabels: {
      type: Boolean,
      default: false,
    },
    styleType: { type: String, default: '' }
  },
  computed: {
    isNotValidateSum() {
      return (typeof this.validateSum === 'number') && (this.validateSum !== (this.value1 + this.value2 + this.value3))
    },
    value1: {
      get() {
        if(this.inputData) {
          return this.inputData[0]
        }
      },
      set(newValue) {
        this.$emit('input', [newValue, this.value2, this.value3])
      }
    },
    value2: {
      get() {
        if(this.inputData) {
          return this.inputData[1]
        }
      },
      set(newValue) {
        this.$emit('input', [this.value1, newValue, this.value3])
      }
    },
    value3: {
      get() {
        if(this.inputData) {
          return this.inputData[2]
        }
      },
      set(newValue) {
        this.$emit('input', [this.value1, this.value2, newValue])
      }
    },
  },
}
</script>

<style lang="scss" scoped>
  @import "../../scss/components/triple-input";
</style>

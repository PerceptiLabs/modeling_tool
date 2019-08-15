<template lang="pug">
  .triple-input
    input.triple-input_input(type="number"
      v-model.number="value1"
    )
    span.triple-input_separate {{ separateSign || 'X'}}
    input.triple-input_input(type="number"
      v-model.number="value2"
    )
    span.triple-input_separate {{ separateSign || 'X' }}
    input.triple-input_input(type="number"
      v-model.number="value3"
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
    }
  },
  computed: {
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
  .triple-input {
    font-size: 1.4rem;
    display: flex;
    align-items: center;
  }
  .triple-input_input {
    max-width: 2.25em;
    min-width: 1.75em;
    padding-right: .15em;
    padding-left: .15em;
  }
  .triple-input_separate {
    margin: 0 .5em;
    &:last-child {
      margin-right: 0;
    }
  }
</style>

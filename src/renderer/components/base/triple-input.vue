<template lang="pug">
  .triple-input
    input.triple-input_input(type="number"
      @input="onChange1($event.target.value)"
      :value="value1"
      )
    template(v-if="value2 !== false")
      span.triple-input_seporate X
      input.triple-input_input(type="number"
        @input="onChange2($event.target.value)"
        :value="value2"
        )
      template(v-if="value3 !== false")
        span.triple-input_seporate X
        input.triple-input_input(type="number"
          @input="onChange3($event.target.value)"
          :value="value3"
          )
</template>

<script>
export default {
  name: "TripleInput",
  props: {
    value1: {type: [String, Number, Boolean], default: false},
    value2: {type: [String, Number, Boolean], default: false},
    value3: {type: [String, Number, Boolean], default: false}
  },
  methods: {
    onChange1(val) {
      this.$emit('setValue1', val)
    },
    onChange2(val) {
      this.$emit('setValue2', val)
    },
    onChange3(val) {
      this.$emit('setValue3', val)
    }
  },
  watch: {
    // resultVal: {
    //   handler: function (val, oldVal) {
    //     this.$emit('setValue', val)
    //   },
    //   deep:true,
    // }
  }
}
</script>

<style lang="scss" scoped>
  .triple-input {
    font-size: 1.4rem;
    display: flex;
    align-items: center;
  }
  .triple-input_input {
    width: 2.25em;
    padding-right: .15em;
    padding-left: .15em;
  }
  .triple-input_seporate {
    margin: 0 .5em;
  }
</style>

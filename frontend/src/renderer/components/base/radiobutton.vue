<template lang="pug">
  label.custom-radio
    input(type="radio"
      :name="groupName"
      :value="valueInput"
      :disabled="disabled"
      v-model="checked"
      @change="onChange()"
      )
    .radio-fake
    .radio-text
      slot

</template>

<script>
export default {
  name: 'BaseRadiobutton',
  props: {
    groupName: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    value: {type: [Boolean, String]},
    valueInput: {String},
  },
  data() {
    return {
      checkedProxy: false
    }
  },
  computed: {
    checked: {
      get() { return this.value },
      set (val) { this.checkedProxy = val }
    }
  },
  methods: {
    onChange() {
      this.$emit('input', this.checkedProxy)
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .custom-radio {
    font-size: 1.2rem;
    display: inline-flex;
    align-items: center;
    padding: .5em 1em .5em 0;

    input[type='radio'] {
      position: absolute;
      left: -9999px;
      opacity: 0;
      width: 1px;
      height: 1px;
      &:checked {
        + .radio-fake {
          background: $bg-grad-blue;
          box-shadow: $icon-shad;
        }
        ~ .radio-text {
          color: $col-txt;
        }
      }
    }
    .radio-fake {
      position: relative;
      flex: 0 0 .6em;
      width: .6em;
      height: .6em;
      cursor: pointer;
      border-radius: 50%;
      background-color: $disable-txt;
    }
    .radio-text {
      font-size: inherit;
      color: $disable-txt;
      margin-left: .75em;
    }
  }
</style>

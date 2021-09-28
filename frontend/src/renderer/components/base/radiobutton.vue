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
  .custom-radio {
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    padding: .25em 1em .25em 0;

    .sidebar-setting-content & {
      font-size: 11px;
    }

    input[type='radio'] {
      position: absolute;
      left: -9999px;
      opacity: 0;
      width: 1px;
      height: 1px;
      &:checked {
        + .radio-fake {
          background: $color-6;
        }
      }
    }
    .radio-fake {
      position: relative;
      flex: 0 0 14px;
      width: 14px;
      height: 14px;
      cursor: pointer;
      border-radius: 50%;
      border: 2px solid #D9E2FF;
      background-color: theme-var($neutral-8);
    }
    .radio-text {
      font-size: inherit;
      color: theme-var($text-highlight);
      margin-left: .75em;
    }
  }
</style>

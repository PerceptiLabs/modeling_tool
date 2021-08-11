<template lang="pug">
  label.custom-radio(:class="{'type-secondary': styleTypeSecondary}")
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
    styleTypeSecondary: {
      type: Boolean,
      value: false,
    }
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
    &.type-secondary {
      .radio-fake {
        position: relative;
        background: transparent;
        flex: 0 0 18px;
        width: 18px;
        height: 18px;
        border: 1px solid #B6C7FB;
        box-sizing: content-box;
      }
      .radio-text {
        font-size: 14px;
        font-family: Roboto, sans-serif;
      }
      input[type='radio'] {
        &:checked {
          + .radio-fake {
            background: transparent;
            border: 1px solid #B6C7FB;
            box-sizing: content-box;
            &:after {
              content: '';
              position: absolute;
              width: 12px;
              height: 12px;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%);
              background-color: #B6C7FB;
              border-radius: 50%;
            }
          }
          ~ .radio-text {
            //color: #fff;
            font-size: 14px;
          }
        }
      }
    }
    
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
          background: #fff;
          border: 1px solid #4D556A;
        }
        ~ .radio-text {
          color: #fff;
        }
      }
    }
    .radio-fake {
      position: relative;
      flex: 0 0 7px;
      width: 7px;
      height: 7px;
      cursor: pointer;
      border-radius: 50%;
      background-color: #4D556A;
    }
    .radio-text {
      font-size: inherit;
      color: #C4C4C4;
      margin-left: .75em;
    }
  }
</style>

<template lang="pug">
  label.custom-checkbox
    .checkbox-text(v-if="labelPosition==='left'")
      slot
    input(type="checkbox"
      :value="valueInput"
      v-model="checked"
      @change="onChange()"
    )
    .checkbox-fake(:class="{'checkbox-fake--icon': iconTheme}")
    .checkbox-text(v-if="labelPosition==='right'")
      slot

</template>

<script>
export default {
  name: 'BaseCheckbox',
  props: {
    value: {type: [Boolean, Array]},
    valueInput: {String},
    labelPosition: {
      type: String,
      default: 'right'
    },
    iconTheme: {
      type: Boolean,
      default: false
    },
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
  .custom-checkbox {
    padding: 0;
    display: inline-flex;
    align-items: center;

    input[type=checkbox] {
      opacity: 0;
      width: 1px;
      height: 1px;
      position: absolute;
      left: -9999px;
      &:checked + .checkbox-fake {
        background: $bg-grad-blue;
        box-shadow: $icon-shad;
        &.checkbox-fake--icon {
          background: $bg-workspace;
          &:after {
            opacity: 1;
          }
        }
      }
      //&:focus + .checkbox-fake {
      //  outline: 1px dotted $col-primary;
      //  box-shadow: 0 0 1px 1px $white;
      //}
    }
    .checkbox-text {
      margin-right: .75em;
      font-size: inherit;
      color: inherit;
    }
    .checkbox-fake {
      width: 1.4em;
      height: 1.4em;
      flex: 0 0 1.4em;
      background-color: $bg-input;
      cursor: pointer;
      position: relative;
      &.checkbox-fake--icon {
        background-color: $bg-workspace;
        &:after {
          content: "\e937";
          font-family: "icomoon";
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          opacity: 0;
          font-size: .9em;
          line-height: 1;
        }
      }
      + .checkbox-text {
        margin-left: .75em;
      }
    }

  }
</style>

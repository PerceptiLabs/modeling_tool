<template lang="pug">
  label.custom-checkbox
    .checkbox-text(v-if="labelPosition==='left'")
      slot
    input(type="checkbox"
      v-model="value"
      data-vv-value-path="value"
      @change="change"
    )
    .checkbox-fake(:class="{'checkbox-fake--icon': iconTheme}")
    .checkbox-text(v-if="labelPosition==='right'")
      slot

</template>

<script>
export default {
  name: 'BaseCheckbox',

  props: {
    // value: {type: [Boolean, Array]},
    // valueInput: {String},
    label: String,
    hasError: Boolean,
    labelPosition: {
      type: String,
      default: 'right'
    },
    iconTheme: {
      type: Boolean,
      default: false
    },
    // // validateName: {
    // //   type: String,
    // //   default: ''
    // // },
    // name: {
    //   type: String,
    //   default: ''
    // },
  },
  mounted () {
    this.$el.value = this.value;
  },
  data() {
    return {
      checkedProxy: false,
      value: null
    }
  },
  watch: {
    value(value) {
      this.$emit('input', value);
    }
  },
  methods: {
    change (event) {
      this.value = event.target.checked ? true : null
    }
  }
  // computed: {
  //   checked: {
  //     get() { return this.value },
  //     set (val) { this.checkedProxy = val }
  //   }
  // },
  // methods: {
  //   onChange() {
  //     this.$emit('input', this.checkedProxy)
  //   }
  // }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .custom-checkbox {
    position: relative;
    display: inline-flex;
    align-items: center;
    padding: 0;

    input[type=checkbox] {
      position: absolute;
      left: -9999px;
      opacity: 0;
      width: 1px;
      height: 1px;
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
      font-size: inherit;
      color: inherit;
      margin-right: .75em;
    }
    .checkbox-fake {
      position: relative;
      flex: 0 0 1.4em;
      width: 1.4em;
      height: 1.4em;
      cursor: pointer;
      background-color: $bg-input;
      &.checkbox-fake--icon {
        background-color: $bg-workspace;
        &:after {
          content: '\e937';
          font-family: 'icomoon';
          font-size: .9em;
          line-height: 1;
          position: absolute;
          top: 50%;
          left: 50%;
          opacity: 0;
          transform: translate(-50%, -50%);
        }
      }
      + .checkbox-text {
        margin-left: .75em;
      }
    }
    .text-error {
      position: absolute;
      top: 100%;
      left: 0;
    }
  }
</style>

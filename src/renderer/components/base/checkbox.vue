<template lang="pug">
  label.custom-checkbox
    .checkbox-text(v-if="labelPosition==='left'")
      slot
    input(type="checkbox")
    .checkbox-fake
    .checkbox-text(v-if="labelPosition==='right'")
      slot

</template>

<script>
export default {
  name: 'BaseCheckbox',
  props: {
    labelPosition: {
      type: String,
      default: 'right'
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
        &:after {
          opacity: 1;
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
      width: 1em;
      height: 1em;
      flex: 0 0 1em;
      background-color: $bg-workspace;
      cursor: pointer;
      position: relative;
      &:after {
        content: "\e937";
        font-family: "icomoon";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        opacity: 0;
        font-size: .5em;
        line-height: 1;
      }
      + .checkbox-text {
        margin-left: .75em;
      }
    }

  }
</style>

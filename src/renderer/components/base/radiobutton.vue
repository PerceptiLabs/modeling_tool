<template lang="pug">
  label.custom-radio
    input(type="radio" :name="groupName")
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
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .custom-radio {
    padding: .5em 1em .5em 0;
    display: inline-flex;
    align-items: center;

    input[type='radio'] {
      opacity: 0;
      width: 1px;
      height: 1px;
      position: absolute;
      left: -9999px;
      &:checked {
        + .radio-fake {
          background: linear-gradient(#7397FE, #6185EE);
          box-shadow: $icon-shad;
        }
        ~ .radio-text {
          color: $col-txt;
        }
      }
      //&:focus + .checkbox-fake {
      //  outline: 1px dotted $col-primary;
      //  box-shadow: 0 0 1px 1px $white;
      //}
    }
    .radio-fake {
      width: .6em;
      height: .6em;
      flex: 0 0 .6em;
      border-radius: 50%;
      background-color: $disable-txt;
      cursor: pointer;
      position: relative;
    }
    .radio-text {
      margin-left: .75em;
      font-size: inherit;
      color: $disable-txt;
    }
  }
</style>

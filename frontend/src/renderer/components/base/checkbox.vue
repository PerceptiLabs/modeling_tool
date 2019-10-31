<template lang="pug">
  label.custom-checkbox
    .checkbox-text(v-if="labelPosition==='left'")
      slot
    input(type="checkbox"
      :disabled="disabled"
      v-model="valueInput"
      @change="change"
    )
    .checkbox-fake(:class="{'checkbox-fake--icon': iconTheme}")
      i.icon.icon-check
    .checkbox-text(v-if="labelPosition==='right'")
      slot

</template>

<script>
export default {
  name: 'BaseCheckbox',

  props: {
    value: Boolean,
    labelPosition: {
      type: String,
      default: 'right'
    },
    disabled: {
      type: Boolean,
      default: false
    },
    iconTheme: {
      type: Boolean,
      default: false
    }
  },
  mounted () {
    this.valueInput = this.value;
  },
  data() {
    return {
      valueInput: null
    }
  },
  methods: {
    change (event) {
      const newValue = event.target.checked;
      this.valueInput = newValue;
      this.$emit('input', newValue);
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .custom-checkbox {
  font-size: 1.2rem;
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
        //background: $bg-grad-blue;
        //box-shadow: $icon-shad;
        .icon {
          opacity: 1;
        }
        /*<!--&.checkbox-fake&#45;&#45;icon {-->*/
        /*<!--  background: $bg-workspace;-->*/
        /*<!--  &:after {-->*/
        /*<!--    opacity: 1;-->*/
        /*<!--  }-->*/
        /*<!--}-->*/
      }
      &:focus + .checkbox-fake {
        outline: 1px dotted $col-primary;
        //box-shadow: 0 0 1px 1px $white;
      }
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
      //background-color: $bg-input;
      background-color: #6E778C;
      .icon {
        font-size: .9em;
        line-height: 1;
        position: absolute;
        top: 50%;
        left: 50%;
        opacity: 0;
        transform: translate(-50%, -50%);
      }
      /*<!--&.checkbox-fake&#45;&#45;icon {-->*/
      /*<!--  background-color: $bg-workspace;-->*/
      /*<!--  &:after {-->*/
      /*<!--    content: '\e937';-->*/
      /*<!--    font-family: 'icomoon';-->*/
      /*<!--    font-size: .9em;-->*/
      /*<!--    line-height: 1;-->*/
      /*<!--    position: absolute;-->*/
      /*<!--    top: 50%;-->*/
      /*<!--    left: 50%;-->*/
      /*<!--    opacity: 0;-->*/
      /*<!--    transform: translate(-50%, -50%);-->*/
      /*<!--  }-->*/
      /*<!--}-->*/
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

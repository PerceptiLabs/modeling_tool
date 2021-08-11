<template lang="pug">
  label.custom-checkbox(:class="{'v-2': isNewUi, 'is-mini-map': isMiniMap, 'disabled': disabled, 'type-secondary': styleTypeSecondary}")
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
    },
    isNewUi: {
      type: Boolean,
      default: false,
    },
    isMiniMap: {
      type: Boolean,
      default: false,
    },
    styleTypeSecondary: {
      type: Boolean,
      default: false,
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
  watch: {
    value: function (newValue){
      this.valueInput = newValue;
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
      background: $color-6;
      .icon {
        opacity: 1;
        color: $black;
      }
      /*<!--&.checkbox-fake&#45;&#45;icon {-->*/
      /*<!--  background: $bg-workspace;-->*/
      /*<!--  &:after {-->*/
      /*<!--    opacity: 1;-->*/
      /*<!--  }-->*/
      /*<!--}-->*/
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
    width: 1.3em;
    height: 1.3em;
    cursor: pointer;
    background-color: $col-txt2;
    border: 0;
    border-radius: 2px;

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

  &.v-2 {
    .checkbox-fake {
      flex: 0 0 13px;
      width: 13px;
      height: 13px;
      background: #383F50;
      border-radius: 2px;
    }
  }
  &.type-secondary {
    .checkbox-fake {
      flex: 0 0 18px;
      width: 18px;
      height: 18px;
      background: transparent;
      border-radius: 2px;
      border: 1px solid #B6C7FB;
    }
    input[type=checkbox] {
      &:checked + .checkbox-fake {
        background-color: #B6C7FB;
      }
    }
    .checkbox-text {
      color: #fff;
      font-size: 14px;
      font-family: 'Roboto', sans-serif;
    }
  }
  &.is-mini-map {
    .checkbox-fake {
      background: #23252A;
    }
  }
  &.disabled {
    pointer-events: none;
    color: gray;
  }
  &.is-silver {
    input[type=checkbox] {
      position: absolute;
      left: -9999px;
      opacity: 0;
      width: 1px;
      height: 1px;
      &:checked + .checkbox-fake {
        background: #EEE;
      }
    }
  }
}
</style>

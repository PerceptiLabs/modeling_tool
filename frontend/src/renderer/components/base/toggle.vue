<template lang="pug">
  label.toggle-button(:class="{'disabled' : disabled}")
    .toggle-fake(@click="onClickToggle" :class="styling")
      .toggle-check(:class="{'selected' : valueInput, 'onoff' : isOne}")

    .toggle-text
      slot

</template>

<script>
export default {
  name: 'BaseToggleButton',

  props: {
    value: Boolean,
    onClick: {
      type: Function,
      default: () => {},
    },
    styling: {
      type: String,
      default: 'normal'
    },
    isOne: {
      type: Boolean,
      default: true
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    color: { 
      type: String,
      default: '#171725'
    },
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
    onClickToggle () {
      if(this.disabled)
        return;
      this.valueInput = !this.valueInput;
      this.$emit('input', true);

      this.onClick();
    }
  }
}
</script>

<style lang="scss" scoped>
  .toggle-button {
    position: relative;
    display: inline-flex;
    align-items: center;
    padding: 0;

    &.disabled {
      pointer-events: none;
      color: gray;
    }
  }

  .toggle-fake {
    position: relative;

    width: 30px;
    height: 16px;

    border: $border-1;
    border-radius: 75px;
    cursor: pointer;

    .toggle-check {
      background: $color-6;
      width: 16px;
      height: 16px;
      position: absolute;
      top: -1px;
      left: 0px;
      border-radius: 50%;

      &.onoff:not(.selected) {
        background: theme-var($border-color);
      }
      &.selected {
        left: unset;
        right: 0px;
      }
    }

    &.large {
      width: 45px;
      height: 24px;

      & .toggle-check {
        width: 24px;
        height: 24px;
      }
    }
  }

  .toggle-text {
    margin-left: 8px;
  }

</style>

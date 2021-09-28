<template lang="pug">
  label.toggle-button
    input(type="checkbox"
      :disabled="disabled"
      v-model="valueInput"
      @change="change"
    )
    .toggle-fake(v-if="icon==='chevron'" :class="{'highlight' : highlight}")
      svg(v-show="!valueInput" width="21" height="21" viewBox="0 0 21 21" fill="none" xmlns="http://www.w3.org/2000/svg")
        circle(cx="10.5" cy="10.5" r="9.5" :stroke="toggleColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round")
        path(d="M15 12L10.5 8L6 12" :stroke="toggleColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round")
      svg(v-show="valueInput" width="21" height="21" viewBox="0 0 21 21" fill="none" xmlns="http://www.w3.org/2000/svg")
        circle(cx="10.5" cy="10.5" r="9.5" :stroke="toggleColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round")
        path(d="M6 9L10.5 13L15 9" :stroke="toggleColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round")
      
    .toggle-text
      slot

</template>

<script>
export default {
  name: 'BaseToggleExpandButton',

  props: {
    value: Boolean,
    icon: {
      type: String,
      default: 'chevron'
    },
    disabled: {
      type: Boolean,
      default: false
    },
    onClick: {
      type: Function,
      default: () => {},
    },
    color: { 
      type: String,
      default: '#171725'
    },
    highlight: {
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
  computed: {
      toggleColor() {
          return this.highlight ? '#FFFFFF' : this.color;
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

      this.onClick();
    }
  }
}
</script>

<style lang="scss" scoped>
  .toggle-button {
    font-size: 1.2rem;
    position: relative;
    display: inline-flex;
    align-items: center;
    padding: 0;
    cursor: pointer;

    input[type=checkbox] {
      position: absolute;
      left: -9999px;
      opacity: 0;
      width: 1px;
      height: 1px;
    }
    &.disabled {
      pointer-events: none;
      color: gray;
    }

  }

  .primary {
    svg path,
    svg circle {
      stroke: $color-6;
    }
  }
</style>

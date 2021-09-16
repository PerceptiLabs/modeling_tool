<template lang="pug">
  button(
    @click="handleClick"
    :class="`base-button base-button-type-${type} base-button-size-${sizes[size]} ${disabled ? 'disabled': ''}`"
    )  
    slot
</template>

<script>

const sizes = {
  1: 's',
  2: 'm',
  3: 'l'
}

export default {
  name: 'BaseButton',
  data() {
    return {
      sizes
    }
  },
  props: {
    size: {
      type: Number,
      default: 2,
    },
    type: { 
      type: String,
      default: 'base',
    },
    disabled: {
      type: Boolean,
      default: false,
    }
  },
  methods: {
    handleClick(event) {
      if(this.disabled) {
        return;
      }
      
      this.$emit('click', event);
    }
  },
};
</script>
<style lang="scss" scoped>
.base-button {
  cursor: pointer;
  font-family: 'Roboto', sans-serif;
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 4px;
  font-size: 16px;
  svg {
    margin-right: 10px;
  }
}
.base-button-type-base {
  background-color: #6185EE;
}
.base-button-type-transparent {
  background-color: transparent;
  border: 1px solid #4D556A;
}

.base-button-size-s {}
.base-button-size-m {
  height: 39px;
}
.base-button-size-l {}

.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>

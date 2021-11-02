<template lang="pug">
div.container
  button.outline(
    v-for="option in options" 
    :key="option.value" 
    @click="onOptionSelect(option.value)" 
    :class="{'active': option.value === value}"
  )
    | {{option.label}}
</template>

<script>
export default {
  props: {
    options: {
      type: Array
    },
    value: String
  },
  methods: {
    onOptionSelect(value) {
      this.$emit("change", value);
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  button {
    flex: 1;
    padding: 12px 20px;

    font-size: 16px;
    line-height: 1;
  }
}
.outline {
  background: transparent;
  color: theme-var($neutral-1);
  outline: none;
  border-style: solid;
  border-width: 2px;
  border-color: theme-var($border-color);

  &:first-child {
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
  }
  &:last-child {
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
  }

  &:not(:last-child):not(.active) {
    border-right-width: 0px;
  }
}

.active {
  border-color: $color-6;
  color: $color-6;

  border-right-width: 1px;
  & + button {
    border-left-width: 0px;
  }
}
</style>

<template lang="pug">
  .help-button-panel-content-item(@click="$emit('handleClick')") 
    span.link-text {{name}}
</template>
<script>
export default {
  name: 'AppHeaderLink',
  props: {
    name: {
      type: String,
      required: true,
    },
  },
};
</script>
<style lang="scss" scoped>
.help-button-panel-content-item {
  margin: 0;
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: normal;
  font-size: 14px;
  line-height: 19px;
  color: $color-bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  white-space: nowrap;
  &:hover {
    color: #6185EE;
  }
}

.help-button-panel-content-item {
  padding: 0.5rem 0;
}
.link-text {
  // margin-left: 2rem;
}
</style>

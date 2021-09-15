<template lang="pug">
  .help-button-panel-content-item(@click="$emit('handleClick')") 
    svg(width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg")
      path(d="M11.3995 1.0009C11.3995 0.724753 11.1756 0.500896 10.8995 0.500896L6.39949 0.500896C6.12335 0.500896 5.89949 0.724754 5.89949 1.0009C5.8995 1.27704 6.12335 1.5009 6.39949 1.5009L10.3995 1.5009L10.3995 5.5009C10.3995 5.77704 10.6234 6.0009 10.8995 6.0009C11.1756 6.0009 11.3995 5.77704 11.3995 5.5009L11.3995 1.0009ZM1.35355 11.2539L11.253 1.35445L10.5459 0.647342L0.646447 10.5468L1.35355 11.2539Z" fill="white")
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
  font-size: 14px;
  line-height: 19px;
  color: #FFFFFF;
  cursor: pointer;
  display: flex;
  align-items: center;
  white-space: nowrap;
}

.help-button-panel-content-item + .help-button-panel-content-item {
  margin-top: 1rem;
}
.link-text {
  margin-left: 2rem;
}
</style>

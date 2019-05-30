<template lang="pug">
  section.sidebar_share
    .sidebar-share_icon.big-text
      i.icon.icon-user
      span Users
    .sidebar-share_btn
      button.btn.btn--primary(type="button"  disabled="disabled") Share


</template>

<script>
export default {
  name: 'SidebarShare',
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .sidebar_share {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: auto;
    padding-top: .5rem;
    padding-bottom: .5rem;
    background: #4b4b5c;
    padding-right: 1.5rem;
    padding-left: 1.5rem;
  }
  .sidebar-share_icon {
    .icon {
      margin-right: .3rem;
    }
  }

</style>

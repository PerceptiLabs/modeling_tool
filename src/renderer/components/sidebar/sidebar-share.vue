<template lang="pug">
  section.sidebar_share.sidebar-content
    .sidebar-share_icon.big-text
      i.icon.icon-user
      span Users
    .sidebar-share_btn
      button.btn.btn--primary(type="button") Share


</template>

<script>
export default {
  name: 'SidebarShare',
  data() {
    return {

    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .sidebar_share {
    background: #4B4B5C;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: .5rem;
    padding-bottom: .5rem;
    margin-top: auto;
  }
  .sidebar-share_icon {
    .icon {
      margin-right: .3rem;
    }
  }
</style>

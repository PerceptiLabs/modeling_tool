<template lang="pug">
  section.sidebar_share.sidebar_content-padding--small
    .sidebar-share_icon.big-text
      //i.icon.icon-user
      //span Users
    //.sidebar-share_btn
      button.btn.btn--primary(type="button"  disabled="disabled") Share
    .sidebar-share_bug-report-btn
      a.btn.btn--primary.report-button(target="_blank" href="https://join.slack.com/t/perceptilabs-com/shared_invite/enQtODQ5NzAwNDkxOTExLWUxODAwZDk0MzA1MmM4OTViNWE4MmVjYjc2OTQwMTQ4N2NmM2ZlYmI5NjZjOWRiYjBkYjBjMTMzNjEyMDNiNDk" :class="{'tutorial-active': activeStepStoryboard === 5}")
        span Report
        i.icon.icon-bug-report


</template>

<script>

  export default {
    name: 'SidebarShare',
    computed: {
      activeStepStoryboard() {
        return this.$store.state.mod_tutorials.activeStepStoryboard
      }
    }
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
  }
  .sidebar-share_icon {
    .icon {
      margin-right: .3rem;
    }
  }
  .sidebar-share_bug-report-btn{
    font-weight: bold;
    .icon {
      font-size: 1.3rem;
    }
  }
  .report-button {
    display: block;
  }
</style>

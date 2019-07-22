<template lang="pug">
  section.sidebar_share.sidebar_content-padding--small
    .sidebar-share_icon.big-text
      //i.icon.icon-user
      //span Users
    //.sidebar-share_btn
      button.btn.btn--primary(type="button"  disabled="disabled") Share
    .sidebar-share_bug-report-btn
      button.btn.btn--primary(type="button" @click="goToLink(`${baseUrlSite}`)")
        span Report
        i.icon.icon-bug-report


</template>

<script>
import { baseUrlSite }    from '@/core/constants.js'
import { goToLink }       from '@/core/helpers.js'

export default {
  name: 'SidebarShare',
  data() {
    return {
      baseUrlSite
    }
  },
  methods: {
    goToLink
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

</style>

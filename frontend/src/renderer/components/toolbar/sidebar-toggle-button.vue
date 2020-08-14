<template lang="pug">
  button.toggle-button(
    :class="{'is-open': isClosed}"
    @click="toggleSidebar()"
    )
    svg.toggle-icon(
      :class="{'is-open': isClosed}"
      xmlns="http://www.w3.org/2000/svg"
      width="14"
      height="13"
      viewBox="0 0 14 13"
      fill="none"
      )
      rect(x="2" y="2" width="10" height="1" rx="0.5" fill="#B6C7FB")
      rect(x="2" y="10" width="10" height="1" rx="0.5" fill="#B6C7FB")
      rect(x="4" y="6" width="8" height="1" rx="0.5" fill="#B6C7FB")
</template>

<script>
import { mapActions } from 'vuex';
export default {
   name: "SidebarToggleButton",
   computed: {
    isClosed() {
      return this.$store.state.globalView.hideSidebar
    },
   },
   methods: {
     ...mapActions({
       openSidebar: 'globalView/hideSidebarAction',
     }),
     toggleSidebar() {
       this.openSidebar(!this.isClosed);
     },
   }
}
</script>

<style lang="scss" scoped>
.toggle-button {
  background: #363E51;
  border-radius: 0px 1px 0px 0px;
  width: 29px;
  height: 29px;
  position:fixed;
  top: 70px;
  right: 0;
}
.toggle-icon {
  transform-origin: 50% 50%;
  &.is-open {
    transform: rotate(-90deg);
  }
}
</style>
  
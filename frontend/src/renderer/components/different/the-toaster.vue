<template lang="pug">
  .toaster-container
    template(v-for="(t,i) in toasts")
      .toast(
        :key="t.networkId + t.type"
        v-if="t.count > 0"
        :class="t.type"
        @click="onToastClick(t)")

        template(v-if="t.type === 'error'")
          .toast-header
            .toast-header-icon
              svg(width="16" height="14" viewBox="0 0 16 14" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M8.00005 0.666504L0.300049 13.9998H15.7L8.00005 0.666504ZM8.66671 5.99984L8.42671 8.99984H7.60672L7.36672 5.99984H8.66671ZM8.00005 11.3332C7.87874 11.3332 7.76016 11.2972 7.6593 11.2298C7.55844 11.1624 7.47982 11.0666 7.4334 10.9545C7.38698 10.8425 7.37483 10.7192 7.3985 10.6002C7.42217 10.4812 7.48058 10.3719 7.56636 10.2861C7.65213 10.2004 7.76142 10.142 7.88039 10.1183C7.99937 10.0946 8.12269 10.1068 8.23476 10.1532C8.34683 10.1996 8.44262 10.2782 8.51002 10.3791C8.57741 10.4799 8.61338 10.5985 8.61338 10.7198C8.61338 10.8825 8.54876 11.0385 8.43374 11.1535C8.31872 11.2686 8.16271 11.3332 8.00005 11.3332Z" fill="#FE7373")

            .toast-header-label Error
            .toast-header-close-button(@click.stop="onClose(t)")
              svg(width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M8.4192 9.03438L6.00281 6.61799L3.5924 9.0284L2.7969 8.2329L5.20731 5.82249L2.7969 3.41208L3.59838 2.61061L6.00879 5.02102L8.4192 2.61061L9.21469 3.4061L6.80428 5.81651L9.22068 8.2329L8.4192 9.03438Z" fill="#5E6F9F")

        template(v-else)
          .toast-header
            .toast-header-icon
              svg(width="16" height="14" viewBox="0 0 16 14" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M8.00005 0.666504L0.300049 13.9998H15.7L8.00005 0.666504ZM8.66671 5.99984L8.42671 8.99984H7.60672L7.36672 5.99984H8.66671ZM8.00005 11.3332C7.87874 11.3332 7.76016 11.2972 7.6593 11.2298C7.55844 11.1624 7.47982 11.0666 7.4334 10.9545C7.38698 10.8425 7.37483 10.7192 7.3985 10.6002C7.42217 10.4812 7.48058 10.3719 7.56636 10.2861C7.65213 10.2004 7.76142 10.142 7.88039 10.1183C7.99937 10.0946 8.12269 10.1068 8.23476 10.1532C8.34683 10.1996 8.44262 10.2782 8.51002 10.3791C8.57741 10.4799 8.61338 10.5985 8.61338 10.7198C8.61338 10.8825 8.54876 11.0385 8.43374 11.1535C8.31872 11.2686 8.16271 11.3332 8.00005 11.3332Z" fill="#6185EE")

            .toast-header-label Warning
            .toast-header-close-button(@click.stop="onClose(t)")
              svg(width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M8.4192 9.03438L6.00281 6.61799L3.5924 9.0284L2.7969 8.2329L5.20731 5.82249L2.7969 3.41208L3.59838 2.61061L6.00879 5.02102L8.4192 2.61061L9.21469 3.4061L6.80428 5.81651L9.22068 8.2329L8.4192 9.03438Z" fill="#5E6F9F")
        .toast-message {{ t.message }}
      br(:key="t.type")

</template>

<script>

export default {
  name: 'TheToaster',
  computed: {
    currentNetworkId() {
      return this.$store.getters['mod_workspace/GET_currentNetworkId'];
    },
    toasts() {
      return this.$store.getters['mod_workspace-notifications/getToasts'](this.currentNetworkId);
    }
  },
  methods: {
    onToastClick(toast) {
      // remove toasts
      this.$store.commit(
        'mod_workspace-notifications/removeToastObjectsForNetwork', 
        { networkId: toast.networkId }
      );
      
      // open notification window 
      this.$store.dispatch('mod_workspace-notifications/setNotificationWindowState', { 
        networkId: this.currentNetworkId, 
        value: true,
        selectedId: null
      });
    },
    onClose(toast) {
      this.$store.commit(
        'mod_workspace-notifications/removeToastObjectsForNetwork', 
        { networkId: toast.networkId }
      );
    }
  }
}
</script>


<style lang="scss" scoped>
$height-status-bar: 5.5rem;

.toaster-container {
  position: fixed;
  transition:all 200ms ease;

  bottom: $height-status-bar;

  z-index: 10;
}

.toast {
  width: 20rem;
  min-height: 6rem;
  max-height: 12rem;

  background: theme-var($neutral-8);
  border: 1px solid $color-6;
  box-sizing: border-box;
  border-radius: 5px;
  padding: 10px 16px; 

  cursor: pointer;

  .toast-header {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;

    .toast-header-icon {
      margin-right: 0.5rem;
    }

    .toast-header-label {
      font-size: 1.4rem;
      color: $color-6;
    }

    .toast-header-close-button {
      margin-left: auto;

      position: relative;

      &:after {
        content: "";
        position: absolute;
        top: -0.5rem;
        left: -0.5rem;
        width: 2rem;
        height: 2rem;
      }
    }
  }


  &.error {
    border: 1px solid $color-danger;
    .toast-header-label {
      color: $color-danger;
    }
  }

  .toast-message {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 1.2rem;
  }
}

</style>
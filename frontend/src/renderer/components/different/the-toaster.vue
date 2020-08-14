<template lang="pug">
  .toaster-container
    template(v-for="(t,i) in toasts")
      .toast(
        :key="t.id"
        @click="onToastClick(t)")

        template(v-if="t.type === 'error'")
          .toast-header
            .toast-header-icon
              svg(width="17" height="16" viewBox="0 0 17 16" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M7.18629 1.38376C7.75651 0.349089 9.24349 0.34909 9.81371 1.38376L16.3676 13.276C16.9186 14.2757 16.1954 15.5 15.0539 15.5H1.9461C0.804634 15.5 0.0814483 14.2757 0.632393 13.276L7.18629 1.38376Z" fill="#FE7373")
                path(d="M7.72977 5.94L9.26977 5.95L8.87977 10.88H8.11977L7.72977 5.94ZM9.19977 11.62V13H7.79977V11.62H9.19977Z" fill="#23252A")
            .toast-header-label Error
            .toast-header-close-button(@click="onClose(t)")
              svg(width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M8.4192 9.03438L6.00281 6.61799L3.5924 9.0284L2.7969 8.2329L5.20731 5.82249L2.7969 3.41208L3.59838 2.61061L6.00879 5.02102L8.4192 2.61061L9.21469 3.4061L6.80428 5.81651L9.22068 8.2329L8.4192 9.03438Z" fill="#5E6F9F")

        template(v-else)
          .toast-header
            .toast-header-icon
              svg(width="17" height="16" viewBox="0 0 17 16" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M7.18629 1.38376C7.75651 0.349089 9.24349 0.34909 9.81371 1.38376L16.3676 13.276C16.9186 14.2757 16.1954 15.5 15.0539 15.5H1.9461C0.804634 15.5 0.0814483 14.2757 0.632393 13.276L7.18629 1.38376Z" fill="#FECF73")
                path(d="M7.72977 5.94L9.26977 5.95L8.87977 10.88H8.11977L7.72977 5.94ZM9.19977 11.62V13H7.79977V11.62H9.19977Z" fill="#23252A")
            .toast-header-label Warning
            .toast-header-close-button(@click="onClose(t)")
              svg(width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M8.4192 9.03438L6.00281 6.61799L3.5924 9.0284L2.7969 8.2329L5.20731 5.82249L2.7969 3.41208L3.59838 2.61061L6.00879 5.02102L8.4192 2.61061L9.21469 3.4061L6.80428 5.81651L9.22068 8.2329L8.4192 9.03438Z" fill="#5E6F9F")
        .toast-message {{ t.message }}
      br(:key="t.id+'1'")
    </template>
  
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
      // remove toast
      this.$store.commit('mod_workspace-notifications/removeToastObject', { id: toast.id });
      // open notification window 

      this.$store.dispatch('mod_workspace-notifications/setNotificationWindowState', { 
        networkId: this.currentNetworkId, 
        value: true,
        selectedId: toast.id
      });
    },
    onClose(toast) {
      this.$store.commit('mod_workspace-notifications/removeToastObject', { id: toast.id });
    }
  }
}
</script>


<style lang="scss" scoped>

$height-status-bar: 3rem;

.toaster-container {
  position: fixed;
  transition:all 200ms ease;

  bottom: $height-status-bar;
  right: 1rem;

  z-index: 10;
}

.toast {
  width: 20rem;
  min-height: 6rem;
  max-height: 12rem;

  background: #363E51;
  border: 1px solid #5E6F9F;
  box-sizing: border-box;
  border-radius: 2px;

  padding: 0.5rem;

  cursor: pointer;

  .toast-header {
    display: flex;
    align-items: center;

    .toast-header-icon {
      margin-right: 0.5rem;
    }

    .toast-header-label {
      font-size: 1.2rem;
    }

    .toast-header-close-button {
      margin-left: auto;
    }
  }

  .toast-message {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

</style>
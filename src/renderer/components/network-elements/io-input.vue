<template lang="pug">
  .net-element
    button.btn.btn--layersbar.layer_parent(type="button"
      @dblclick="openPopup"
      @contextmenu="openSettings"
    )
      i.icon.icon-data-in

    .net-element_popup(v-if="popupIsOpen")
      h1 popup info
    .net-element_settings(v-if="settingsIsOpen")
      h1 popup settings
</template>

<script>
export default {
  name: 'IoInput',
  data() {
    return {
      popupIsOpen: false,
      settingsIsOpen: false
    }
  },
  methods: {
    openPopup() {
        this.popupIsOpen = true
    },
    openSettings() {
      this.settingsIsOpen = true
    }
  }
}
</script>

<style lang="scss" scoped>
  .net-element {
  }
  .net-element_popup,
  .net-element_settings {
    position: absolute;
    left: 100%;
    top: 0;
  }
  .net-element_settings {

  }
</style>

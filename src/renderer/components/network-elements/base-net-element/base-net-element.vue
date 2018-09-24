<template lang="pug">
  .net-element(
    :style="style"
    :class="active || isActive ? 'active' : 'inactive'"
    @mousedown.stop.prevent="bodyDown($event)"
    @touchstart.stop.prevent="bodyDown($event)"
    @dblclick="openPopup"
    @contextmenu="openSettings"
    )
    slot

    .net-element_popup(v-if="popupIsOpen")
      slot(name="popup")
        h1 popup info

    .net-element_settings(v-if="settingsIsOpen")
      h1 popup settings

</template>
<script src="./base-net-element.js"></script>
<style lang="scss" scoped>
  @import "./base-net-element.scss";
</style>

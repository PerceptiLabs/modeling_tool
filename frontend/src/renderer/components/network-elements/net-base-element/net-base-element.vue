<template lang="pug">
  .net-element.js-clickout(tabindex="0"
    ref="rootBaseElement"
    :style="style"
    :id="dataEl.layerMeta.tutorialId"
    :class="classEl"

    @mousedown="switchMousedownEvent($event)"
    @click="switchClickEvent($event)"
    @dblclick.stop.prevent="switchDblclick($event)"
    @contextmenu.stop.prevent="openContext($event)"
    )
    .net-element_be-for-end(v-if="beForEnd") {{ beForEnd }}
    .net-element_checkpoint-icon(v-if="showCheckpoint")


    .net-element_code-error(v-if="dataEl.layerCodeError")
      i.icon.icon-code-error

    .net-element_arrows-start(v-if="showDotsArrow")
      button.arrows-start_btn(type="button" @mousedown="startArrowPaint($event)")
    .net-element_arrows-start.net-element_arrows-start--right(v-if="showDotsArrow")
      button.arrows-start_btn(type="button" @mousedown="startArrowPaint($event)")
    .net-element_arrows-start.net-element_arrows-start--bottom(v-if="showDotsArrow")
      button.arrows-start_btn(type="button" @mousedown="startArrowPaint($event)")
    .net-element_arrows-start.net-element_arrows-start--left(v-if="showDotsArrow")
      button.arrows-start_btn(type="button" @mousedown="startArrowPaint($event)")

    .net-element_btn(ref="BaseElement")
      slot

    .net-element_window(
      v-if="settingsIsOpen"
      :class="classElWindow"
      :style="styleElWindow"
      ref="elementSettings"
      )
      slot(name="settings")

    .net-element_window.net-element_context-menu(
      v-if="contextIsOpen"
      :class="classElWindow"
      :style="styleElWindow"
      )
      context-menu(
        :data-el="dataEl"
        @open-settings.stop="switchDblclick($event)"
        )

</template>

<script src="./net-base-element.js"></script>

<style lang="scss" scoped>
  @import "../../../scss/base";
  @import "./net-base-element";
</style>

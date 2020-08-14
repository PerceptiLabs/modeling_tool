<template lang="pug">
  .net-element.js-clickout(tabindex="0"
    ref="rootBaseElement"
    :style="style"
    :openLayerContainer="openLayerContainer"
    :id="dataEl.layerMeta.tutorialId"
    :layer-id="dataEl.layerId"
    :class="classEl"

    @mousedown="switchMousedownEvent($event)"
    @click="switchClickEvent($event)"
    @dblclick.stop.prevent="switchDblclick($event)"
    @contextmenu.stop.prevent="openContext($event)"
    )
    .net-element_be-for-end(
      v-if="beForEnd"
      ) {{ beForEnd }}
    .net-element_checkpoint-icon(v-if="showCheckpoint")

    .net-element_code-error(v-if="dataEl.layerCodeError")
      i.icon.icon-code-error

    i.icon.icon-layer-settings.openContainer(
      v-if="dataEl.componentName === 'LayerContainer'"
      @click="openLayerContainer"
      )

    //- .net-element_arrows-start(v-if="showDotsArrow")
    //-   button.arrows-start_btn(type="button" @mousedown="startArrowPaint($event)")
    //- .net-element_arrows-start.net-element_arrows-start--right(v-if="showDotsArrow")
    //-   button.arrows-start_btn(type="button" @mousedown="startArrowPaint($event)")
    //- .net-element_arrows-start.net-element_arrows-start--bottom(v-if="showDotsArrow")
    //-   button.arrows-start_btn(type="button" @mousedown="startArrowPaint($event)")
    //- .net-element_arrows-start.net-element_arrows-start--left(v-if="showDotsArrow")
    //-   button.arrows-start_btn(type="button")

    .net-element_btn(
      ref="BaseElement"
      )
      slot
    settings-preview(
        :current-el="dataEl"
      )
    //- pre {{JSON.parse(JSON.stringify(this.$store.getters['mod_workspace/GET_networkElementConnectionInChartData'](dataEl.layerId) || {}), 1)}}
    //- div.variable-area
    //- .net-element_window(
    //-   v-if="settingsIsOpen"
    //-   :class="classElWindow"
    //-   ref="elementSettings"
    //-   )
    //-   slot(name="settings")

    //- .net-element_window.net-element_context-menu(
    //-   v-if="contextIsOpen"
    //-   :class="classElWindow"
    //-   )
    //-   context-menu(
    //-     :data-el="dataEl"
    //-     @open-settings.stop="switchDblclick($event)"
    //-     )

</template>

<script src="./net-base-element.js"></script>

<style lang="scss" scoped>
  @import "../../../scss/base";
  @import "./net-base-element";
  .variable-area {
    height: 31px;
    background: #23252A;
    border: 1px solid #3F4C70;
    border-radius: 0px 0px 2px 2px
  }
</style>

<template lang="pug">
.net-element.js-clickout(
  tabindex="0",
  ref="rootBaseElement",
  :style="style",
  :openLayerContainer="openLayerContainer",
  :id="dataEl.layerMeta && dataEl.layerMeta.tutorialId",
  :layer-id="dataEl.layerId",
  :class="classEl",
  @mousedown="switchMousedownEvent($event)",
  @click="switchClickEvent($event)",
  @dblclick.stop.prevent="switchDblclick($event)",
  @contextmenu.stop.prevent="openContext($event)"
)
  .net-element_be-for-end(v-if="beForEnd") {{ beForEnd }}
  .net-element_checkpoint-icon(v-if="showCheckpoint")

  .net-element_code-error(v-if="dataEl.layerCodeError")
    i.icon.icon-code-error

  i.icon.icon-layer-settings.openContainer(
    v-if="dataEl.componentName === 'LayerContainer'",
    @click="openLayerContainer"
  )
  .net-element_btn(ref="BaseElement")
    slot
  settings-preview(:current-el="dataEl")
</template>

<script src="./net-base-element.js"></script>

<style lang="scss" scoped>
@import "./net-base-element";
.variable-area {
  height: 31px;
  background: theme-var($neutral-8);
  border: $border-1;
  border-radius: 0px 0px 2px 2px;
}
</style>

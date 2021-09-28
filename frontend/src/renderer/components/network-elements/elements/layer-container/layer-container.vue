<template lang="pug">
  .layer-container(v-if="showChildContainer")
    base-net-el(
      v-if="isOpenContainer"
      :data-el="elementData"
      :layer-container="true"
      @open-container="toggleContainer(false)"
    )
      view-el(:current-el="elementData" :withLayerTypeText="withLayerTypeText")
    template(v-else)
      .layer-container_box(
        :style="containerStyle"
        )
        h4.layer-container_title(
          :style="zoomingStyle"
        ) {{ elementData.layerName }}
        button.layer-container_btn-open.btn.btn--link.icon.icon-layer-settings(
          type="button"
          @click.stop="toggleContainer(true)"
          @contextmenu.stop.prevent="openContext($event)"
        )
        .net-element_window.net-element_context-menu(
          v-if="contextIsOpen"
          :class="classElWindow"
        )
          context-menu(
            :data-el="elementData"
            @open-settings.stop="toggleContainer(true)"
          )
      //-component(
        v-for="el in elementData.containerLayersList"
        /:key="el.layerId"
        /:is="el.componentName"
        /:element-data="el"
        )

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ViewEl       from './view-layer-container.vue';
  import ContextMenu        from '@/components/network-elements/net-context-menu/net-context-menu.vue';
  import { widthElement } from '@/core/constants.js'
  import {mapActions} from "vuex";

  export default {
    name: 'LayerContainer',
    components: { BaseNetEl, ViewEl, ContextMenu },
    props: {
      elementData: Object,
     withLayerTypeText: Boolean,
    },
    destroyed() {
      document.removeEventListener('click', this.closeContext, true);
      document.removeEventListener('contextmenu', this.closeContext, true);
    },
    data() {
      return {
        contextIsOpen: false,
        openWinPosition: {
          left: false,
          top: true,
          offset: 0
        },
        buttonStyle: {}
      }
    },
    watch: {
      isOpenContainer() {
        this.contextIsOpen = false;
      }
    },
    computed: {
      networkScale() {
        return this.$store.getters['mod_workspace/GET_currentNetworkZoom'];
      },
      zoomingStyle() {
        let scale = `scale(${this.networkScale})`;
        
        let style = {
          'transform': scale,
          'transform-origin': 'right bottom'
        };

        return style;
      },
      containerStyle() {
        let arrTop = [];
        let arrLeft = [];
        let rootNet = this.currentNetList;
        let net = {};
        
        // let containerZIndex = 40;
        let containerHaveOpenSubContainer = false;
        let acumulator = collectPositionRecursion(this.elementData.containerLayersList, []);

        arrTop = acumulator.map(position => position[0]);
        arrLeft = acumulator.map(position => position[1]);

        const minLeft = Math.min(...arrLeft);
        const minTop = Math.min(...arrTop);
        let padding = 30;

        // if container have a sub-container open it should be padded with x2
        if(containerHaveOpenSubContainer)
          padding += 30;

        const widthEl = widthElement * this.networkScale;
        padding *= this.networkScale;

        return {
          // zIndex: containerZIndex,
          left: minLeft - padding + 'px',
          width: Math.max(...arrLeft) - minLeft + widthEl + padding*2 + 'px',
          top: minTop - padding + 'px',
          height: Math.max(...arrTop) - minTop + widthEl + padding*2 + 'px',
        };

        // fn is collecting [top, left] position and check if container have open sub-container
        function collectPositionRecursion(net, data) {
          for(let elId in  net) {
            const el = rootNet[elId];
            if(el.layerType === 'Container' && el.layerNone) {
              collectPositionRecursion(el.containerLayersList, data);
              containerHaveOpenSubContainer = true;
              // containerZIndex = containerZIndex - 2;
            }

            data.push([el.layerMeta.position.top, el.layerMeta.position.left]);
          }
          return data;
        }
      },
     
      currentNetList() {
        return this.$store.getters['mod_workspace/GET_currentNetworkElementList']
      },
      showChildContainer() {
        return this.elementData.isShow;
      },
      isOpenContainer() {
        return !this.elementData.layerNone
      },
      classElWindow() {
        return {
          'net-element_window--left': this.openWinPosition.left,
          'net-element_window--top': this.openWinPosition.top
        }
      }
    },
    methods: {
      ...mapActions({
        elementSelect:   'mod_workspace/SET_elementSelect'
      }),
      toggleContainer(val) {
        this.$store.dispatch('mod_workspace/TOGGLE_container', {val, container: this.elementData})
      },
      closeContext() {
        this.contextIsOpen = false;
        document.removeEventListener('click', this.closeContext, true);
        document.removeEventListener('contextmenu', this.closeContext, true);
        return false;
      },
      openContext(event) {
        this.contextIsOpen = true;
        this.elementSelect({id: this.elementData.layerId, setValue: true, resetOther: true });
        document.addEventListener('click', this.closeContext, true);
        document.addEventListener('contextmenu', this.closeContext, true);
      },
    }
  }
</script>
<style lang="scss" scoped>
  
  .layer-container_box {
    position: absolute;
    border-radius: $bdrs;
    background-color: #2B2F35;
    border: 1px solid $toolbar-border;
    box-shadow: $box-shad;
  }
  .layer-container_title {
    position: absolute;
    bottom: 100%;
    right: 0;
    margin-bottom: 1rem;
    background-color: rgba($bg-workspace, .5);
    transform: translate3d(0,0,0);
  }
  .layer-container_btn-open {
    position: absolute;
    bottom: 1rem;
    right: 1rem;
    z-index: 3;
    color: #9af142;
  }

  .net-element_window {
    position: absolute;
    z-index: 10;
    top: 0;
    left: 100%;
    padding-left: 10px;
    padding-right: 10px;
    &.net-element_window--left {
      left: auto;
      right: 100%;
    }
    &.net-element_window--top {
      top: auto;
      bottom: 0;
    }
  }
</style>

<template lang="pug">
  .layer-container
    base-net-el(
      v-if="isOpenContainer"
      :data-el="elementData"
      :layer-container="true"
      @open-container="toggleContainer(false)"
    )
      view-el
      template(slot="context")
        context-menu
    template(v-else)
      .layer-container_box(
        :style="containerStyle"
        )
        h4.layer-container_title {{ elementData.layerName }}
        button.layer-container_btn-open.btn.btn--link.icon.icon-layer-net-set.net-element-layercontainer(type="button"
          @dblclick="toggleContainer(true)"
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
  import ContextMenu  from '@/components/network-elements/net-context-menu/net-context-menu.vue';
  import ViewEl       from './view-layer-container.vue';


  export default {
    name: 'LayerContainer',
    components: {
      BaseNetEl, ContextMenu, ViewEl,
    },
    props: {
      elementData: Object
    },
    mounted() {
      //console.log(this.elementData);
    },
    data() {
      return {
        //isOpenContainer: true
      }
    },
    computed: {
      containerStyle() {
        let arrTop = [];
        let arrLeft = [];
        let net = this.elementData.containerLayersList;
        for(let elId in  net) {
          const el = net[elId];
          arrTop.push(el.layerMeta.position.top);
          arrLeft.push(el.layerMeta.position.left);
        }
        const minLeft = Math.min(...arrLeft);
        const minTop = Math.min(...arrTop);
        const padding = 30;
        const widthEl = 60;
        return {
          left: minLeft - padding + 'px',
          width: Math.max(...arrLeft) - minLeft + widthEl + padding*2 + 'px',
          top: minTop - padding + 'px',
          height: Math.max(...arrTop) - minTop + widthEl + padding*2 + 'px',
        }
      },
      isOpenContainer() {
        return !this.elementData.layerNone
      }
    },
    methods: {
      toggleContainer(val) {
        this.$store.dispatch('mod_workspace/TOGGLE_container', {val, container: this.elementData})
      }
    }
  }
</script>
<style lang="scss" scoped>
  @import "../../../../scss/base";
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
    right: 1rem;
    margin-bottom: 1rem;
    background-color: rgba($bg-workspace, .5);
    transform: translate3d(0,0,0);
  }
  .layer-container_btn-open {
    position: absolute;
    bottom: 1rem;
    right: 1rem;
    z-index: 3;
  }
</style>
<template lang="pug">
  section.sidebar_layers
    .layers_title.d-flex.sidebar_content-padding--small
      //-i.icon.icon-burger.middle-text
      h3 Layers
    //-.layers_meta.sidebar-content
      .form_row
        .input-wrap_icon
          input(type="text" placeholder="Enter the name of layer" disabled="disabled")
          i.icon.icon-search
        button.btn.btn--icon(type="button" disabled="disabled")
          i.icon.icon-folder
        button.btn.btn--icon(type="button"  disabled="disabled"
          @click="deleteElement"
        )
          i.icon.icon-delete

    perfect-scrollbar(tag='ul').layers_body(ref="layersItemList")
      sidebar-layers-item(
        v-for="item in networkElementList"
        :key="item.layerId"
        ref="sidebarLayersItem"
        :item-data="item"
        )



</template>

<script>
import SidebarLayersItem from '@/components/sidebar/sidebar-layers--item.vue'
import {mapGetters, mapMutations} from 'vuex';

export default {
  name: 'SidebarLayers',
  components: {
    SidebarLayersItem
  },
  computed: {
    ...mapGetters({
      workspace: 'mod_workspace/GET_currentNetwork',
      currentSelectedList: 'mod_workspace/GET_currentSelectedEl',
    }),
    networkElementList() {
      let currentNet = this.$store.getters['mod_workspace/GET_currentNetworkElementList'];
      var newNet = {...currentNet};
      clearContainer(currentNet);

      const keysArrayNewNet = Object.keys(newNet);
      const lastElement = newNet[keysArrayNewNet[keysArrayNewNet.length -1]];

      if(lastElement && lastElement.componentName === 'LayerContainer' && lastElement.parentContainerID) {
        const duplicateElement = document.getElementById(lastElement.layerId);
        duplicateElement.classList.add('hide-duplicate-element');
      }

      function clearContainer(net) {
        for(let idEl in net) {
          let el = net[idEl];
          if(el.componentName === 'LayerContainer') {
            let delKeys = Object.keys(el.containerLayersList);
            if(!delKeys.length) continue;
            delKeys.forEach((id)=> {
              if(newNet[id] && newNet[id].componentName !== 'LayerContainer') delete newNet[id]
            });
          }
        }
      }
      return newNet
    },
    isGridEnabled: {
      get() {
        return this.$store.state.globalView.isGridEnabled 
      },
      set(value) {
        this.setGridValue(value);
      }
    },
  },
  watch: {
    currentSelectedList(newList) {
      if(!newList.length) return;
      const layersItemList = this.$refs.layersItemList;
      const layersItemListHeight = layersItemList.clientHeight;
      const layersItemListHeightScroll = layersItemList.scrollHeight;
      if(layersItemListHeight === layersItemListHeightScroll) return;
      const layersItemListOffset = layersItemList.offsetTop;
      const listTop = layersItemList.scrollTop;
      const listBottom = listTop + layersItemListHeight;
      const domEl = this.$refs.sidebarLayersItem.find((el)=>el.currentId === newList[0].layerId);
      const domTop = domEl.$el.offsetTop - layersItemListOffset;
      if(!(domTop > listTop && domTop < listBottom)) layersItemList.scroll(0, domTop);
    }
  },
  methods: {
    ...mapMutations({
      setGridValue: 'globalView/setGridStateMutation'
    }),
    deleteElement() {
      // let currentSelect =  this.networkElementList.findIndex((item)=> {
      //   return item.meta.isSelected === true;
      // });
    }

  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .sidebar_layers {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    max-height: 80vh;
    overflow: hidden;
    background-color: $bg-toolbar;
    box-sizing: border-box;
    border: 1px solid $toolbar-separator-color;
    border-radius: 2px;
  }
  .layers_title {
    align-items: center;
    flex: 0 0 auto;
    height: $h-sidebar-layers-item;
    h3 {
      font-size: 12px;
      margin: 0;
      color: $color-12;
    }
  }
  .layers_body {
    overflow: auto;
    flex: 1;
  }
  .layers_meta {
    flex: 0 0 auto;
    height: $h-sidebar-layers-item;
    border-bottom: 1px solid $bg-toolbar;
  }
  .layers_actions {
    padding-bottom: 1rem;
    text-align: right;
    .btn {
      font-size: 1.2857em;
      + .btn {
        margin-left: 1.7857rem;
      }
    }
  }
  .layers_search {
    align-items: center;
    .icon-filter {
      font-size: 1.5714rem;
      margin-right: 1rem;
      padding: .25rem;
    }
    input {
      box-shadow: $icon-shad;
    }
  }
  .hide-duplicate-element {
    display: none;
  }
  .form_row {
    padding: 10px 15px;
  }
</style>

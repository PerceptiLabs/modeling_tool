<template lang="pug">
  section.sidebar_layers
    .layers_title.bold.d-flex.sidebar_content-padding--small
      span Components
      base-toggle-expand.primary(:value="showComponents" :onClick="toggleShowComponents")
    perfect-scrollbar(tag='ul').layers_body(ref="layersItemList" v-if="showComponents")
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
      networkElementListLength: 'mod_workspace/GET_currentNetworkElementListLength',      
      showComponents: 'mod_workspace/GET_showComponents',
    }),
    networkElementList() {
      let currentNet = this.$store.getters['mod_workspace/GET_currentNetworkElementList'];
      var newNet = {...currentNet};
      let filterItemsWithThoseId = filterItemIdsRecursion(newNet,  []);
      
      
      function filterItemIdsRecursion(net, data) {
        for(let elId in  net) {
          const el = net[elId];
          if(el.layerType === 'Container') {
            data = [...data, ...Object.keys(el.containerLayersList)];
          }
          
        }
        return data;
      }
      
      
      filterItemsWithThoseId.map(id => {
        delete newNet[id];
      });
      
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
  methods: {
    ...mapMutations({
      setGridValue: 'globalView/setGridStateMutation',
      setShowComponents: 'mod_workspace/setShowComponentsMutation'
    }),
    toggleShowComponents () {
      this.setShowComponents(!this.showComponents)
    }
  }
}
</script>

<style lang="scss" scoped>
  
  .sidebar_layers {
    display: flex;
    flex-direction: column;
    // flex-grow: 1;
    max-height: 25vh;
    overflow: hidden;
    // background-color: $bg-toolbar;
    box-sizing: border-box;
    // border: 1px solid $toolbar-separator-color;
    border-radius: 2px;
    &.training {
      max-height: calc(100vh - 600px);
    }   
    
    border-bottom: $border-1;
    padding-top: 8px;
    padding-bottom: 8px;
  }
  .layers_title {
    display: flex;
    align-items: center;
    flex: 0 0 auto;
    justify-content: space-between;
    height: $h-sidebar-layers-item;
    span {
      font-size: 16px;
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
  .primary {
    margin-left: 16px;
  }
</style>

<template lang="pug">
  section.sidebar_layers
    .layers_title.d-flex.sidebar_content-padding--small
      i.icon.icon-burger.middle-text
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

    .layers_body
      sidebar-layers-item(
        v-for="item in networkElementList"
        :key="item.layerId"
        :item-data="item"
        )




</template>

<script>
import SidebarLayersItem from '@/components/sidebar/sidebar-layers--item.vue'
import {mapGetters} from 'vuex';

export default {
  name: 'SidebarLayers',
  components: {
    SidebarLayersItem
  },
  computed: {
    ...mapGetters({
      workspace: 'mod_workspace/GET_currentNetwork',
      //networkElementList: 'mod_workspace/GET_currentNetworkElementList',
    }),
    networkElementList() {
      let currentNet = this.$store.getters['mod_workspace/GET_currentNetworkElementList'];
      var newNet = {...currentNet};
      clearContainer(currentNet);

      function clearContainer(net) {
        for(let idEl in net) {
          let el = net[idEl];
          if(el.componentName === 'LayerContainer') {
            let delKeys = Object.keys(el.containerLayersList);
            if(!delKeys.length) continue;
            delKeys.forEach((id)=> {
              if(newNet[id].componentName !== 'LayerContainer') delete newNet[id]
            })
          }
        }
      }
      return newNet
    }
  },
  methods: {
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
    max-height: 50vh;
    border-bottom: 1px solid $bg-toolbar;
  }
  .layers_title {
    align-items: center;
    flex: 0 0 auto;
    height: $h-sidebar-layers-item;
    h3 {
      margin: 0 0 0 .5em;
    }
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
</style>

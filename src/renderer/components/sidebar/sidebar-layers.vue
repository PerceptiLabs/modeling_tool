<template lang="pug">
  section.sidebar_layers
    .layers_title.sidebar-content.d-flex
      i.icon.icon-burger.middle-text
      h3 Layers
    //
    .layers_body
      div
        .layer-item-wrap
          .layer-item
            .layer-item_title
              span {{ workspace.networkName }}

        sidebar-layers-item(
          v-for="(item, i) in workspace.network"
          :key="item.i"
          :itemData="item"
          :itemIndex="[i]")

    .layers_meta.sidebar-content
      .layers_actions

        button.btn.btn--icon(type="button" disabled="disabled")
          i.icon.icon-folder
        button.btn.btn--icon(type="button"  disabled="disabled"
          @click="deleteElement"
          )
          i.icon.icon-delete

      .layers_search.d-flex
        i.icon.icon-filter
        .input-wrap_icon
          input(type="text" placeholder="Enter the name of layer" disabled="disabled")
          i.icon.icon-search


</template>

<script>
import SidebarLayersItem from '@/components/sidebar/sidebar-layers--item.vue'

export default {
  name: 'SidebarLayers',
  components: {
    SidebarLayersItem
  },
  mounted() {

  },
  data() {
    return {

    }
  },
  computed: {
    workspace() {
      return this.$store.state.mod_workspace.workspaceContent[this.currentNetwork]
    },
    currentNetwork() {
      return this.$store.state.mod_workspace.currentNetwork
    },
  },
  methods: {
    deleteElement() {
      let currentSelect =  this.workspace.network.findIndex(function(item) {
        //console.log(item);
        return item.meta.isSelected === true;
      });
      //console.log(currentSelect);
    }
  }
}
</script>

<style lang="scss">
  @import "../../scss/base";

  .sidebar_layers {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    max-height: 50vh;
  }
  .sidebar-content {
    padding-left: $h-sidebar-layers-indent;
    padding-right: $h-sidebar-layers-indent;
  }
  .layers_title {
    flex: 0 0 auto;
    align-items: center;
    height: $h-sidebar-layers-item;
    border-bottom: 1px solid $bg-toolbar;
    h3 {
      margin: 0 0 0 .5em;
    }
  }
  .layers_body {
    flex: 1 1 100%;
    display: flex;
    flex-direction: column;
    > div {
      flex: 1 1 100%;
      overflow: auto;
    }
  }
  .layers_meta {
    padding-top: .6429em;
    padding-bottom: 2em;
    flex: 0 0 auto;
    border-top: 1px solid $bg-toolbar;
    border-bottom: 1px solid $bg-toolbar;
  }
  .layers_actions {
    text-align: right;
    padding-bottom: 1rem;
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
      padding: .25rem;
      margin-right: 1rem;
    }
    .input-wrap_icon {
      //margin-left: .5em;
    }
    input {
      box-shadow: $icon-shad;
    }
  }
</style>

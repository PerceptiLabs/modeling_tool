<template lang="pug">
  section.sidebar_layers
    .layers_title.sidebar-content.d-flex
      i.icon.icon-burger.middle-text
      h3 Layers
    //
    .layers_body(v-bar)
      div
        sidebar-layers-item(
          v-for="(item, i) in workspace.network"
          :key="item.i"
          :itemData="item"
          :itemIndex="[i]")



        //sl-vue-tree(
          v-model='nodes'
          ref='slVueTree'
          //:allow-multiselect='false'
          //:draggable="false"
          //@select='nodeSelected'
          //@drop='nodeDropped'
          //@toggle='nodeToggled'
          )

          template(
            slot="title"
            slot-scope="{ node }"
            )
            span.item-icon
              i.icon.icon-folder(v-if='!node.isLeaf')
            | {{ node.title }}

          template(
            slot="toggle"
            slot-scope="{ node }"
            )
            span.sl_folder-icon(
              v-if='!node.isLeaf'
              //:class="{'open': !node.isExpanded}"
              )
              i.icon.icon-shevron

          template(
            slot='sidebar'
            slot-scope='{ node }'
            )
            button.btn.btn--icon.sl_visible-icon.sl_visible-icon--lock( type="button"
              @click='event => toggleLocking(event, node)'
              //:class="{'invisible-icon': node.data && node.data.lock === false}"
              )
              i.icon.icon-lock
            button.btn.btn--icon.sl_visible-icon.sl_visible-icon--visiblity( type="button"
              @click='event => toggleVisibility(event, node)'
              /:class="{'invisible-icon': node.data && node.data.visible === false}"
              )
              i.icon.icon-eye
            button.btn.btn--icon.sl_icon-sidebar-left(type="button")
              i.icon.icon-empty
      //div
        sl-vue-tree(v-model="test2")
        //v-jstree(
          //:data="test"
          //:draggable="true"
          //:show-checkbox="true"
          //:multiple="true"
          //:allow-batch="true"
          //:whole-row="true"
          @item-click="itemClick")


    .layers_meta.sidebar-content
      .layers_actions
        button.btn.btn--icon(type="button")
          i.icon.icon-folder
        button.btn.btn--icon(type="button")
          i.icon.icon-delete
      .layers_search.d-flex
        i.icon.icon-filter
        .input-wrap_icon
          input(type="text" placeholder="Enter the name of layer")
          i.icon.icon-search


</template>

<script>
import SlVueTree  from 'sl-vue-tree'
import SidebarLayersItem from '@/components/sidebar/sidebar-layers--item.vue'

export default {
  name: 'SidebarLayers',
  components: {
    SlVueTree,
    SidebarLayersItem
  },
  mounted() {
    window.slVueTree = this.$refs.slVueTree;
  },
  data() {
    return {
      // nodes: [
      //   {
      //     title: 'Folder2',
      //     isExpanded: true,
      //     isDragging: false,
      //     //isDraggable: false,
      //     //isSelectable: false,
      //     data: {
      //       visible: false,
      //       lock: false
      //     },
      //     children: [
      //       {
      //         title: 'Item3',
      //         isLeaf: true,
      //         //isDraggable: false,
      //         //isSelectable: false,
      //         data: {
      //           visible: false,
      //           lock: false
      //         },
      //       },
      //       {
      //         title: 'Item4',
      //         isLeaf: true,
      //         //isDraggable: false,
      //         //isSelectable: false,
      //       },
      //       {
      //         title: 'Folder3',
      //         //isDraggable: false,
      //         //isSelectable: false,
      //         children: [
      //           {
      //             title: 'Item5',
      //             isLeaf: true
      //           }
      //         ]
      //       }
      //     ]
      //   },
      //   {
      //     title: 'Item6',
      //     isLeaf: true,
      //     //isDraggable: false,
      //     //isSelectable: false,
      //
      //   },
      //   {
      //     title: 'Item7',
      //     isLeaf: true,
      //     //isDraggable: false,
      //     //isSelectable: false,
      //
      //     data: {
      //       visible: false
      //     }
      //   },
      // ]
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
    toggleVisibility: function (event, node) {
      const slVueTree = this.$refs.slVueTree;
      event.stopPropagation();
      const visible = !node.data || node.data.visible !== false;
      slVueTree.updateNode(node.path, {data: { visible: !visible}});
    },
    toggleLocking: function (event, node) {
      const slVueTree = this.$refs.slVueTree;
      event.stopPropagation();
      const lock = !node.data || node.data.lock !== false;
      slVueTree.updateNode(node.path, {data: { lock: !lock}});
    },
    nodeSelected(nodes, event) {
      //this.lastEvent = `Select nodes: ${nodes.map(node => node.title).join(', ')}`;
    },
    nodeToggled(node, event) {
      //this.lastEvent = `Node ${node.title} is ${ node.isExpanded ? 'expanded' : 'collapsed'}`;
    },
    nodeDropped(nodes, position, event) {
      //this.lastEvent = `Nodes: ${nodes.map(node => node.title).join(', ')} are dropped ${position.placement} ${position.node.title}`;
    },
    // showContextMenu(node, event) {
    //   event.preventDefault();
    //   this.contextMenuIsVisible = true;
    //   const $contextMenu = this.$refs.contextmenu;
    //   $contextMenu.style.left = event.clientX + 'px';
    //   $contextMenu.style.top = event.clientY + 'px';
    // },
    removeNode() {
      this.contextMenuIsVisible = false;
      const $slVueTree = this.$refs.slVueTree;
      const paths = $slVueTree.getSelected().map(node => node.path);
      $slVueTree.remove(paths);
    }
  }
}
</script>

<style lang="scss">
  @import "../../scss/base";

  .sidebar_layers {
    display: flex;
    flex-direction: column;
    //flex: 0 0 59vh;
    height: 59vh;
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

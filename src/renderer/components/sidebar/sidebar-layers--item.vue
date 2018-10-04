<template lang="pug">
  .layer-item-wrap
    .layer-item(
      :class="{'selected': itemData.meta.isSelected}"
      @click="setSelect(itemIndex)"
      )
      .layer-item_left-sidebar
        button.btn.btn--icon(type="button")
          i.icon.icon-empty
      .layer-item_folder-section(:class="{'open': isOpen}")
        button.btn.btn--icon(type="button"
          v-if="itemData.child"
          @click="toggleOpen()"
        )
          i.icon.icon-shevron
          i.icon.icon-folder
      .layer-item_title
        span {{ itemData.layerName }}
      .layer-item_right-sidebar
        button.btn.btn--icon.sl_visible-icon.sl_visible-icon--lock( type="button"
          :class="{'invisible-icon': itemData.meta.isInvisible}"
        )
          i.icon.icon-lock
        button.btn.btn--icon.sl_visible-icon.sl_visible-icon--visiblity( type="button"
          :class="{'invisible-icon': itemData.meta.isLock}"
        )
          i.icon.icon-eye
    .layer-item_child-list(
      :class="{'open': isOpen}"
      v-if="itemData.child"
      )
      sidebar-layers-item(
        v-for="(item, i) in itemData.child"
        :key="item.i"
        :itemData="item"
        :itemIndex="[itemIndexPath, i]"
        )


</template>

<script>
  import SidebarLayersItem from '@/components/sidebar/sidebar-layers--item.vue'

export default {
  name: 'SidebarLayersItem',
  components: {
    SidebarLayersItem
  },
  props: {
    itemData: {
      type: Object,
      default: function () {
        return null
      }
    },
    itemIndex: {
      type: [Number, Array]
    },
  },
  mounted() {

  },
  data() {
    return {
      isOpen: false
    }
  },
  computed: {
    itemIndexPath() {
      console.log(this.itemIndex);
      if(Array.isArray(this.itemIndex)) {
        return [].concat.apply([], this.itemIndex.map(i => i instanceof Array ? i : [i]))
      }
      else {
        return this.itemIndex
      }
    }
  },
  methods: {
    setSelect(index) {
      console.log(index);
    },
    toggleOpen() {
      this.isOpen = !this.isOpen
    },
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
  .layer-item-wrap {

  }
  .layer-item {
    position: relative;
    display: flex;
    align-items: center;
    height: $h-sidebar-layers-item;
    padding-left: $h-sidebar-layers-indent;
    padding-right: $h-sidebar-layers-indent;
    border: 1px solid transparent;
    border-bottom: 1px solid $bg-toolbar;
    &:hover {
      color: white;
    }
    &.selected {
      background-color: #697187;
    }
    .icon {
      display: block;
    }
  }

  .layer-item_left-sidebar {
    .btn {
      padding: .5em;
      font-size: 1.2em;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
  .layer-item_folder-section {
    .btn {
      padding: 0;
      display: flex;
      align-items: center;
    }
    &.open {
      .icon-shevron {
        transform: rotate(0);
      }
    }
    .icon-shevron {
      font-size: 1.2em;
      transform: rotate(-90deg);
    }
    .icon-folder {
      font-size: 1.4286em;
      margin-left: .6em;
    }
  }
  .layer-item_title {
    padding-left: .5em;
  }
  .layer-item_right-sidebar {
    display: flex;
    align-items: center;
    margin-left: auto;
    .visible-icon--lock {
      font-size: 1.2857em;
    }
    .visible-icon--visiblity {
      font-size: 1.7143em;
    }
  }
  .visible-icon {
    padding: 0 .9rem;
    &.invisible-icon {
      color: $disable-txt;
    }
  }
  .layer-item_child-list {
    display: none;
    .layer-item_folder-section {
      padding-left: 2em;
    }
    &.open {
      display: block;
    }
  }

  .layer-item_child-list .layer-item_child-list {
    .layer-item_folder-section {
      padding-left: 4em;
    }
  }
  .layer-item_child-list .layer-item_child-list .layer-item_child-list {
    .layer-item_folder-section {
      padding-left: 6em;
    }
  }
</style>

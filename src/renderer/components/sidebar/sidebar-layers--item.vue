<template lang="pug">
  .layer-item-wrap
    .layer-item.js-clickout(
      :class="{'selected': itemData.layerMeta.isSelected}"
      @click="setSelect($event)"
      )
      .layer-item_left-sidebar()
        button.btn.btn--icon(type="button")
          i.icon.icon-empty
      .layer-item_folder-section(:class="{'open': isOpen}")
        i(v-if="itemData.child").icon.icon-folder
        //button.btn.btn--icon(type="button"
          v-if="itemData.child"
          @click="toggleOpen()"
          )
          i.icon.icon-shevron
          i.icon.icon-folder
      .layer-item_title
        text-editable(
          :text-title="itemData.layerName"
          @changeTitle="editElName"
          )
      .layer-item_right-sidebar
        button.btn.btn--icon.visible-icon.visible-icon--lock( type="button"
          :class="{'invisible-icon': !itemData.layerMeta.isLock}"
          @click="toggleLock()"
        )
          i.icon.icon-lock
        //-button.btn.btn--icon.visible-icon.visible-icon--visiblity( type="button"
          /:class="{'invisible-icon': itemData.layerMeta.isInvisible}"
          /@click="toggleVisible(itemIndex)"
          )
          i.icon.icon-eye
    //-.layer-item_child-list(
      /:class="{'open': isOpen}"
      v-if="itemData.child"
      )
      sidebar-layers-item(
        v-for="(item, i) in itemData.child"
        /:key="item.i"
        /:itemData="item"
        /:itemIndex="currentNode(i)"
        )


</template>

<script>
  import SidebarLayersItem  from '@/components/sidebar/sidebar-layers--item.vue'
  import TextEditable       from '@/components/base/text-editable.vue'
  import clickOutside       from '@/core/mixins/click-outside.js'

export default {
  name: 'SidebarLayersItem',
  mixins: [clickOutside],
  components: {
    SidebarLayersItem,
    TextEditable
  },
  props: {
    itemData: {
      type: Object,
      default: function () {
        return null
      }
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
    statisticsIsOpen() {
      return this.$store.getters['mod_workspace/GET_statisticsIsOpen']
    },
    currentId() {
      return this.itemData.layerId
    }
  },
  methods: {
    // currentNode(item) {
    //   let childNode = this.itemIndex.slice();
    //   childNode.push(item);
    //   return childNode
    // },
    toggleOpen() {
      this.isOpen = !this.isOpen
    },
    setSelect(ev) {
      //console.log(ev);
      if (this.statisticsIsOpen) {
        console.log('TODO add functions');
        //this.$store.commit('mod_statistics/CHANGE_selectElArr', this.dataEl)
      }
      else {
        this.ClickElementTracking = ev.target.closest('.js-clickout');
        document.addEventListener('click', this.clickOutside);
        this.$store.dispatch('mod_workspace/SET_elementSelect', {id: this.currentId, setValue: true});
      }
    },
    clickOutsideAction() {
      if (!this.statisticsIsOpen) {
        this.deselect()
      }
    },
    toggleLock() {
      this.$store.commit('mod_workspace/SET_elementLock', this.itemData.layerId);
      this.deselect();
    },
    toggleVisible() {
      this.$store.commit('mod_workspace/SET_elementVisible', this.itemData.layerId);
    },
    editElName(newName) {
      this.$store.commit('mod_workspace/SET_elementName', { id: this.currentId, setValue: newName });
    },
    deselect() {
      this.$store.dispatch('mod_workspace/SET_elementSelect', { id: this.currentId, setValue: false });
    },
  }
}
</script>

<style lang="scss">
  @import "../../scss/base";
  .layer-item {
    position: relative;
    display: flex;
    align-items: center;
    height: $h-sidebar-layers-item;
    padding-right: $h-sidebar-layers-indent;
    padding-left: $h-sidebar-layers-indent;
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
      font-size: 1.2em;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: .5em;
    }
  }
  .layer-item_folder-section {
    .btn {
      display: flex;
      align-items: center;
      padding: 0;
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
    //flex: 1;
    //height: 100%;
    //line-height: $h-sidebar-layers-item;
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

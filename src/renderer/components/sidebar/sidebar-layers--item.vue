<template lang="pug">
  .layer-item-wrap
    .layer-item.js-clickout(
      :class="{'selected': itemData.layerMeta.isSelected}"
      @click="setSelect($event)"
      )
      .layer-item_left-sidebar
        button.btn.btn--icon.layer-item--btn-action(type="button")
          i.icon.icon-empty

      .layer-item_main
        button.btn.btn--icon.layer-item-left_btn-folder.layer-item--btn-action(type="button"
          v-if="itemData.componentName === 'LayerContainer'"
          :class="{'open': openContainer}"
          @click="toggleOpen()"
        )
          i.icon.icon-shevron-right
        text-editable.layer-item_title.ellipsis(
          :text-title="itemData.layerName"
          @change-title="editElName"
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
    .layer-item_child-list(
      :class="{'open': openContainer}"
      v-if="itemData.componentName === 'LayerContainer'"
      )
      sidebar-layers-item(
        v-for="(item, i) in itemData.containerLayersList"
        :key="item.i"
        :item-data="item"
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
      //isOpen: false
    }
  },
  computed: {
    statisticsIsOpen() {
      return this.$store.getters['mod_workspace/GET_statisticsIsOpen']
    },
    currentId() {
      return this.itemData.layerId
    },
    openContainer() {
      return this.itemData.layerNone
    }
  },
  methods: {
    toggleOpen() {
      this.$store.dispatch('mod_workspace/TOGGLE_container', {val: this.openContainer, container: this.itemData})
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
    flex: 0 0 auto;
    display: flex;
    align-items: center;
  }
  .layer-item--btn-action {
    font-size: 1.2em;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: .5em;
  }
  .layer-item-left_btn-folder {
    .icon-shevron-right {
      transform: rotate(0);
    }
    &.open .icon-shevron-right{
      transform: rotate(90deg);
    }
  }
  .layer-item_main {
    flex: 1 1 100%;
    display: flex;
    align-items: center;
    overflow: hidden;
  }
  .layer-item_title {
    padding-left: .5rem;
  }
  .layer-item_right-sidebar {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
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
    &.open {
      display: block;
    }
    .layer-item_main {
      padding-left: 3em;
    }
    .layer-item_child-list {
      .layer-item_main {
        padding-left: 6em;
      }
      .layer-item_child-list {
        .layer-item_main {
          padding-left: 9em;
        }
      }
    }
  }
</style>

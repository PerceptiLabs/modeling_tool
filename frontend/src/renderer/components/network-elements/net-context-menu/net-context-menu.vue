<template lang="pug">
ul.action-list
  li
    button.action-list_btn(type="button", @mousedown="openSettings($event)")
      span.action-list_btn-text(
        v-if="dataEl.componentName === 'LayerContainer'"
      ) {{ dataEl.layerNone ? 'Close Group' : 'Open Group' }}
      span.action-list_btn-text(v-else) Open layer
      span DblClick
  li
    button.action-list_btn(type="button", @mousedown="deleteElement")
      span.action-list_btn-text Delete
      span Del
  li.action-list_item-line
  li(v-if="dataEl.componentName !== 'LayerContainer'")
    button.action-list_btn(type="button", @mousedown="addLayerContainer")
      span.action-list_btn-text Add group
      span Ctrl + G
  li(v-else)
    button.action-list_btn(
      type="button",
      @mousedown.stop="unGroupLayerContainer"
    )
      span.action-list_btn-text Ungroup
      span
</template>

<script>
export default {
  name: "NetContextMenu",
  props: {
    dataEl: {
      type: Object,
      default: function() {
        return {};
      }
    }
  },
  data() {
    return {};
  },
  methods: {
    openSettings(ev) {
      this.$emit("open-settings", ev);
    },
    deleteElement() {
      this.$store.dispatch("mod_workspace/DELETE_element");
    },
    addLayerContainer() {
      this.$store.dispatch("mod_workspace/ADD_container");
    },
    unGroupLayerContainer() {
      this.$store.dispatch("mod_workspace/UNGROUP_container", this.dataEl);
    }
  }
};
</script>

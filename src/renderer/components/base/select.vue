<template lang="pug">
  .custom-select
    button.custom-select_view.input.clickout(type="button"
      @click="openList($event)"
      )
      span {{ selected }}
      i.icon.icon-shevron
    ul.custom-select_option-list.action-list(v-if="isOpenList")
      li.custom-select_option.action-list_btn(
        v-for="(option, i) in selectOptions"
        :key="i"
        @click="selectedOption(option)"
      )
        span.action-list_btn-text {{ option }}

</template>

<script>
  import clickOutside from '@/core/mixins/click-outside.js'

export default {
  name: "BaseSelect",
  mixins: [clickOutside],
  props: {
    selectOptions: {
      type: Array,
      default: function () {
        return []
      }
    }
  },
  data() {
    return {
      isOpenList: false,
      selected: '',
    }
  },
  methods: {
    clickOutsideAction() {
      this.closeList()
    },
    openList(ev) {
      this.ClickElementTracking = ev.target.closest('.clickout');
      document.addEventListener('click', this.clickOutside);
      this.isOpenList ? this.closeList() : this.isOpenList = true
    },
    closeList() {
      this.isOpenList = false;
    },
    selectedOption(value) {
      this.selected = value;
      this.closeList();
      this.$emit('select', value)
    },
  }
}
</script>

<style lang="scss" scoped>
  .custom-select {
    position: relative;

  }
  .custom-select_view {
    cursor: default;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .custom-select_option-list {
    position: absolute;
    z-index: 1;
    top: 0;
    left: 0;
  }
  .custom-select_option {
    cursor: default;
  }
</style>

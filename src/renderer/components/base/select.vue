<template lang="pug">
  .custom-select
    button.custom-select_view.input(type="button"
      :class="{'open-list': isOpenList}"
      @click="openList"
      @blur="closeList"
      )
      span {{ selectedText }}
      i.icon.icon-shevron

    ul.custom-select_option-list.action-list(v-if="isOpenList")
      button.custom-select_option.action-list_btn(type="button"
        v-for="(option, i) in selectOptions"
        :key="i"
        @mousedown="selectedOption(option.value)"
      )
        span.action-list_btn-text {{ option.text }}

</template>

<script>
export default {
  name: "BaseSelect",
  props: {
    value: {
      type: String,
      default: ''
    },
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
      selectedText: '',
    }
  },
  watch: {
    value: {
      handler(newVal) {
        if(this.selectOptions.length && newVal) {
          let index = this.selectOptions.findIndex((el)=>el.value === newVal);
          this.selectedText = this.selectOptions[index].text;
        }
      },
      immediate: true
    }
  },
  methods: {
    openList() {
      this.isOpenList ? this.closeList() : this.isOpenList = true
    },
    closeList() {
      this.isOpenList = false;
    },
    selectedOption(opt) {
      this.closeList();
      this.$emit('input', opt)
    },
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .custom-select {
    width: 100%;
    position: relative;
  }
  .custom-select_view {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: default;
    .icon {
      transform: rotate(90deg);
    }
    &.open-list {
      .icon {
        transform: rotate(-90deg);
      }
    }
  }
  .custom-select_option-list {
    position: absolute;
    z-index: 1;
    top: 100%;
    left: 0;
    //overflow: visible;
    //&:after {
    //  content: '';
    //  position: absolute;
    //  bottom: 100%;
    //  right: .7rem;
    //  border: 1rem solid transparent;
    //  border-bottom-color: $bg-toolbar;
    //}
  }
  .custom-select_option {
    cursor: default;
    &:first-child {
      border-radius: $bdrs $bdrs 0 0;
    }
    &:last-child {
      border-radius: 0 0 $bdrs $bdrs;
    }
  }
</style>

<template lang="pug">
  .settings-arrow(
    :style="position"
  )
    button.settings-arrow_view(type="button"
      @click="openList"
    )
      span {{ checkedOptions }}

    ul.settings-arrow_option-list.action-list(v-if="isOpenList")
      li.settings-arrow_option(
        v-for="(option, i) in selectOptions"
        :key="i"
      )
        label.action-list_btn
          input.action-list_input(
            type="radio"
            :name="uniqName"
            :value="option.value"
            v-model="checkedOptions"
          )
          span.action-list_icon.icon.icon-ellipse
          .action-list_bg
          span.action-list_btn-text {{ option.text }}

</template>

<script>

export default {
  name: "SettingsArrow",
  props: {
    arrowData: {
      type: Object
    }
  },
  mounted() {
    //if(this.value.length) this.checkedOptions = this.value
  },
  beforeDestroy() {
    this.checkedOptions = null;
  },
  data() {
    return {
      isOpenList: false,
      checkedOptions: 'O',
      selectOptions: [
        { text: 'Output',  value: 'O' },
        { text: 'Weights',  value: 'W' },
        { text: 'Bias',  value: 'B' }
      ],
    }
  },
  computed: {
    position() {
      return {
        left: this.arrowData.positionArrow.path.settings.x + 'px',
        top: this.arrowData.positionArrow.path.settings.y + 'px'
      }
    },
    uniqName() {
      return this._uid + 'selectid'
    },
  },
  watch: {
    checkedOptions(newVal, oldVal) {
      if(oldVal === null) return;
      this.closeList();
    },
  },
  methods: {
    openList() {
      this.isOpenList ? this.closeList() : this.isOpenList = true
    },
    closeList() {
      this.isOpenList = false;
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../../scss/base";
  .settings-arrow {
    position: absolute;
    z-index: 3;
    transform: translate(-50%, -50%);
  }
  .settings-arrow_view {
    width: 1.5rem;
    height: 1.5rem;
    border-radius: 50%;
    background-color: $col-primary;
    color: $bg-workspace;
    padding: 0;
  }
  .settings-arrow_option-list {
    min-width: 100px;
    position: absolute;
    z-index: 2;
    top: 75%;
    left: 50%;
    max-height: 13.5rem;
    overflow: auto;
  }
  .settings-arrow_option {
    &:first-child {
      border-radius: $bdrs $bdrs 0 0;
    }
    &:last-child {
      border-radius: 0 0 $bdrs $bdrs;
    }
  }
  .action-list_btn {
    position: relative;
    justify-content: flex-start;
  }
  .action-list_input {
    position: absolute;
    left: -9999px;
    opacity: 0;
    &:not(:checked) + .action-list_icon {
      opacity: 0;
    }
    &:checked ~ .action-list_bg {
      position: absolute;
      z-index: -1;
      background-color: #6E778C;
      left: 0;
      right: 0;
      top: 0;
      bottom: 0;
    }
  }
  .action-list_icon {
    margin-right: 1rem;
    color: $col-primary;
  }
</style>
<template>
  <div 
    :class="['cell-container', { 'focused': isFocused }]"
    @click="onCellContainterClick">

    <component :is="cellType" v-bind="{cell, isFocused}" />
  </div>
</template>


<script>
import CodeCell from "@/components/notebooks/notebook-cell-code.vue";
import MarkdownCell from "@/components/notebooks/notebook-cell-markdown.vue";

export default {
  components: {
    CodeCell,
    MarkdownCell
  },
  props: {
    cell: {
      default: ""
    },
    isFocused: {
      default: false
    }
  },
  methods: {
    onCellContainterClick() {
      // this.$emit('click', this.cell.hashCode);
    }
  },
  computed: {
    cellType() {
      if (this.cell.hasOwnProperty('Output')) {
        return CodeCell;
      } else {
        return MarkdownCell;
      }
    }
  }
};
</script>

<style lang="scss" scoped>
@import '../../scss/base/_variables.scss';

$border-width: 3px;

.cell-container {
  width: calc(100% - 10rem);

  margin: 0 auto;

  background-color: $bg-workspace;
  color: $color-6;

  font-family: monospace;

  border: 1px solid transparent;
  border-left: $border-width solid transparent;

  &:hover {
    border-left: $border-width solid $white;
  }

  &.focused {
    border: 1px solid $col-primary2;
    border-left: $border-width solid $col-primary2;
  }
}

</style>

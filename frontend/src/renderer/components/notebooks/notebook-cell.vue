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
$border-width: 5px;
$col-primary2: #6E92FA;

.cell-container {
  width: 70rem;

  margin: 0 auto;

  background-color: #d9d9d9;
  color: #282d39;

  font-family: monospace;

  border: 1px solid transparent;
  border-left: $border-width solid transparent;

  &:hover {
    border-left: $border-width solid #4D556A;
  }

  &.focused {
    border: 1px solid $col-primary2;
    border-left: $border-width solid $col-primary2;
  }
}

</style>

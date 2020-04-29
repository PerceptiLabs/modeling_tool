<template>
  <div class="cell-contents">
    <div class="cell-input">
      <div :class="['cell-input-operation-count', {'focused': isFocused}]">In [ {{ cell.execution_count || '&nbsp;' }} ]:</div>
      <CodeHQ 
        class="cell-input-code"
        :value="cell.Output" 
        :autofocus="false" 
        :lineNumbers="false"
        :styleActiveLine="false"
        :mode="codeMirrorMode" 
        :maxWidth="'100%'" />
    </div>
    
    <div 
      class="cell-output"
      v-if="cell.outputs && cell.outputs.length">
      <div class="cell-output-gutter"></div>
      <div class="cell-output-contents">
        {{ cell.outputs[0].text  }}
      </div>
    </div>
  </div>
</template>


<script>
import CodeHQ from "@/components/network-elements/elements-settings/code-hq.vue";

export default {
  components: {
    CodeHQ
  },
  props: {
    cell: {
      required: true,
      type: Object
    },
    isFocused: {
      type: Boolean
    }
  },
  methods: {
    onCellContainterClick() {
      this.$emit('click', this.cell.hashCode);
    }
  },
  computed: {
    codeMirrorMode() {
      if (!this.cell) { return ''; }
      else if (this.cell.hasOwnProperty('Output')) { return 'text/x-python'; }
      else if (cell.cell_type === "markdown") { return 'gfm'; }
      else { return ''; }
    }
  }
};
</script>

<style lang="scss" scoped>
@import '../../scss/base/_variables.scss';

$cell-left-gutter: 6.6rem;

.cell-contents {
  font-family: Roboto;
  font-style: normal;
  font-weight: normal;
  font-size: 12px;
  padding: 0.5rem;

  .cell-input {
    display: flex;
    background-color: $bg-workspace;

    .cell-input-operation-count {
      flex-basis: $cell-left-gutter;
      flex-shrink: 0;
      padding-top: 0.75rem;
      padding-right: 1rem;
      text-align: right;
    }

    .cell-input-code {
      flex-grow: 1;
      padding: 0.5rem 1rem 0.5rem 0;
      border-radius: 2px;

      /deep/ .CodeMirror {
        background-color: $bg-workspace;
      }
    }
  }

  .cell-output {
    margin-top: 1rem 0;
    white-space: pre-wrap;

    display: flex;
    // border-left: 1px solid transparent;

    .cell-output-gutter {
      width: $cell-left-gutter;
    }

    .cell-output-contents{
      padding: 0.5rem 0;  
    }
  }
}

</style>

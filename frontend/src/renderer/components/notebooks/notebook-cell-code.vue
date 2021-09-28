<template>
  <div class="cell-contents">
    <div class="cell-input">
      <div class="cell-input-operation-count">In [ {{ cell.execution_count || '&nbsp;' }} ]:</div>
      <codeEditor 
        :class="['cell-input-code', {'focused': isFocused}]"
        :code="cell.Output"
        :readOnly="true"
        :autoUpdateEditorHeight="true"
        :scrollBeyondLastLine="false"
        :handleMouseWheel="false" />
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
import codeEditor from '@/components/different/code-editor.vue';

export default {
  components: { codeEditor },
  props: {
    cell: {
      required: true,
      type: Object
    },
    isFocused: {
      type: Boolean
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
$cell-left-gutter: 6.6rem;

.cell-contents {
  font-family: Roboto;
  font-style: normal;
  font-weight: normal;
  font-size: 12px;
  padding: 0 0.5rem;

  .cell-input {
    display: flex;
    background-color: transparent;

    .cell-input-operation-count {
      flex-basis: $cell-left-gutter;
      flex-shrink: 0;
      padding-top: 0.9rem;
      padding-right: 1rem;
      text-align: right;
      background-color: transparent;
      color: $toolbar-button-border;
    }

    .cell-input-code {
      padding: 0.5rem 1rem 0.5rem 1rem;
      border-radius: 2px;
      border: 1px solid $bg-toolbar;
      box-sizing: border-box;
      border-radius: 2px;
      
      &.focused {
        border: 1px solid $color-6;
      }
    }
  }

  .cell-output {
    margin-top: 1rem 0;
    white-space: pre-wrap;

    display: flex;

    .cell-output-gutter {
      width: $cell-left-gutter;
    }

    .cell-output-contents{
      padding: 0.5rem 0;  
    }
  }
}

</style>

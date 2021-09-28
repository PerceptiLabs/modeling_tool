<template lang="pug">
  .editor(ref="code-editor")
</template>

<script>
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api';
import { mapState } from 'vuex';
import { THEME_DARK } from '@/core/constants.js';

export default {
  name: 'CodeEditor',
  props: {
    code: String,
    errorRow: { type: [Number, String] },
    readOnly: {
      type: Boolean,
      default: false
    },
    scrollBeyondLastLine: {
      type: Boolean,
      default: true
    },
    autoUpdateEditorHeight: {
      type: Boolean,
      default: false
    },
    handleMouseWheel: {
      type: Boolean,
      default: true
    },
  },
  computed: {
    ...mapState({
      theme:                      state => state.globalView.theme
    }),
  },
  data() {
    return {
      editorInstance: null,
      decorations: []
    }
  },
  methods: {
    initEditor() {
      this.editorInstance = monaco.editor.create(this.$refs['code-editor'], {
        value: '',
        language: 'python',
        theme: this.theme === THEME_DARK ? 'vs-dark' : 'vs-light',
        readOnly: this.readOnly,
        scrollBeyondLastLine: this.scrollBeyondLastLine,
        scrollbar: {
          handleMouseWheel: this.handleMouseWheel,
        },
        minimap: {
          enabled: false
        },
      });

      this.isFocusedContextKey = this.editorInstance.createContextKey('isFocused', false);

      this.editorInstance.onDidFocusEditorText(() => {
        this.$emit('focus');
      });
      this.editorInstance.onDidBlurEditorText(() => {
        this.$emit('blur');
      });
      this.editorInstance.onDidChangeModelContent((e) => {
        this.$emit('input', this.editorInstance.getValue());
      });

      if (this.autoUpdateEditorHeight) {
        this.editorInstance.onDidContentSizeChange(() => this.updateHeight());
      }
    },
    setCodeContent() {
      this.editorInstance.setValue(this.code || this.content);
    },
    setupBindings() {
      // "Bindings" are just the Monaco term for extra events handlers

      // The documentation tells us to dispose the bindings, but what's returned 
      // from the addCommand() method is just a number (so .dispose is impossible
      // to call from it)...

      // CTRL + S
      this.editorInstance.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S, () => {
        this.$emit('save-shortcut');
      });
    },
    markErrorRow() {
      if(!this.errorRow || !this.editorInstance) { return; }
      // Currently only marks single rows
      
      this.decorations = this.editorInstance.deltaDecorations(this.decorations, [
        { 
          range: new monaco.Range(this.errorRow,1,this.errorRow,1),
          options: { isWholeLine: true, className: 'has-error', marginClassName: 'has-error' }
        },
      ]);

      this.editorInstance.revealLineInCenter(this.errorRow);
    },
    clearErrorRow() {
      if(this.errorRow || !this.editorInstance || !this.decorations) { return; }
      
      const errorElements = document.querySelectorAll('.has-error');

      this.editorInstance.deltaDecorations(this.decorations, [
        { range: new monaco.Range(1, 1, 1, 1), options: {}},
      ]);
    },
    updateHeight() {
      // This is for the notebook view, where there is specific height set.
      // We set the editor to be as long as the content.
      if(!this.editorInstance) { return; }
 
      const contentWidth = this.$refs['code-editor'].getBoundingClientRect().width;
      const contentHeight = this.editorInstance.getContentHeight();

      this.editorInstance.layout({ width: contentWidth, height: contentHeight });
    },
    handleResize() {
      // This is to handle CMD + plus/minus operations.
      this.editorInstance.layout();
    }
  },
  mounted() {
    if (this.$refs) {

      this.initEditor();
      
      this.setupBindings();
      this.setCodeContent();

      window.addEventListener('resize', this.handleResize);
    }
  },
  beforeDestroy() {
    this.editorInstance.dispose();
    window.removeEventListener('resize', this.handleResize);
  },
  watch: {
    errorRow: {
      handler(value) {
        this.$nextTick(() => {
          this.markErrorRow();
          this.clearErrorRow();
        });

      },
      immediate: true
    },
    theme: {
      handler(value) {
        monaco.editor.setTheme(value === THEME_DARK ? 'vs-dark' : 'vs-light')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.editor {
  position: relative;
  width: calc(100% - 4rem);
  height: 100%;

  box-sizing: border-box;
  background: theme-var($neutral-8);

  margin: 1rem;
}

/deep/ .has-error {
  background-color: rgba(255, 0, 0, 0.3);
}
</style>
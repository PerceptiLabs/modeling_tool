<template lang="pug">
  .code-hq
    textarea(
      ref="textarea"
      :name="name"
      :placeholder="placeholder"
      )
</template>

<script>
  // lib
  import CodeMirror from 'codemirror/lib/codemirror.js';
  import 'codemirror/mode/python/python.js'
  // theme css
  import 'codemirror/lib/codemirror.css'
  //import 'codemirror/theme/monokai.css'
  //import 'codemirror/theme/base16-dark.css' //#5B657B
  // require active-line.js
  import'codemirror/addon/selection/active-line.js'
  // closebrackets
  import'codemirror/addon/edit/closebrackets.js'
  // keyMap
  // import'codemirror/mode/clike/clike.js'
  // import'codemirror/addon/edit/matchbrackets.js'
  // import'codemirror/addon/comment/comment.js'
  // import'codemirror/addon/dialog/dialog.js'
  // import'codemirror/addon/dialog/dialog.css'
  // import'codemirror/addon/search/searchcursor.js'
  // import'codemirror/addon/search/search.js'
  // import'codemirror/keymap/emacs.js'

  // export
  export default {
    name: 'codeHq',
    props: {
      code: String,
      value: String,
      marker: Function,
      unseenLines: Array,
      name:         {type: String,   default: 'code-hq'},
      placeholder:  {type: String,   default: ''},
      merge:        {type: Boolean,  default: false },
      // options:   {type: Object,   default: () => ({})},
      events:       {type: Array,    default: () => ([])},
      globalOptions:{type: Object,   default: () => ({})},
      globalEvents: {type: Array,    default: () => ([])},

      errorRow: {type: Number }
    },
    mounted() {
      this.initialize();
      this.$nextTick(() => {
        this.cminstance.refresh();

        if(this.errorRow) {
          this.cminstance.markText(
            { line: this.errorRow - 1,  ch: 0 },
            { line: this.errorRow,      ch: 0 },
            { className: "code-row_error" }
          );
        }
      })
    },
    beforeDestroy() {
      this.destroy()
    },
    data() {
      return {
        content: '',
        codemirror: null,
        cminstance: null,
        options: {
          autoCloseBrackets: true,
          tabSize: 4,
          styleActiveLine: true,
          lineNumbers: true,
          line: true,
          mode: 'text/x-python',
          theme: "monokai",
        }
      }
    },

    watch: {
      // options: {
      //   deep: true,
      //   handler(options) {
      //     for (const key in options) {
      //       this.cminstance.setOption(key, options[key])
      //     }
      //   }
      // },
      // merge() {
      //   this.$nextTick(this.switchMerge)
      // },
      code(newVal) {
        this.handerCodeChange(newVal)
      },
      value(newVal) {
        this.handerCodeChange(newVal)
      },
    },
    methods: {
      initialize() {
        const cmOptions = Object.assign({}, this.globalOptions, this.options);
        if (this.merge) {
          this.codemirror = CodeMirror.MergeView(this.$refs.mergeview, cmOptions);
          this.cminstance = this.codemirror.edit
        }
        else {
          this.codemirror = CodeMirror.fromTextArea(this.$refs.textarea, cmOptions);
          this.cminstance = this.codemirror;
          this.cminstance.setValue(this.code || this.value || this.content)
        }
        this.cminstance.on('change', cm => {
          this.content = cm.getValue();
          if (this.$emit) {
            this.$emit('input', this.content)
          }
        });

        const tmpEvents = {};
        const allEvents = [
          'scroll', 'changes', 'beforeChange', 'cursorActivity', 'keyHandled', 'inputRead', 'electricInput',
          'beforeSelectionChange', 'viewportChange', 'swapDoc', 'gutterClick', 'gutterContextMenu',
          'focus', 'blur', 'refresh', 'optionChange', 'scrollCursorIntoView', 'update'
        ]
        .concat(this.events)
        .concat(this.globalEvents)
        .filter(e => (!tmpEvents[e] && (tmpEvents[e] = true)))
        .forEach(event => {

          this.cminstance.on(event, (...args) => {

            this.$emit(event, ...args);
            const lowerCaseEvent = event.replace(/([A-Z])/g, '-$1').toLowerCase();
            if (lowerCaseEvent !== event) {
              this.$emit(lowerCaseEvent, ...args)
            }
          })
        });

        this.$emit('ready', this.codemirror);
        this.unseenLineMarkers();

        // prevents funky dynamic rendering
        this.refresh()
      },
      refresh() {
        this.$nextTick(() => {
          this.cminstance.refresh()
        })
      },
      destroy() {
        // garbage cleanup
        const element = this.cminstance.doc.cm.getWrapperElement();
        element && element.remove && element.remove()
      },
      handerCodeChange(newVal) {
        const cm_value = this.cminstance.getValue();
        if (newVal !== cm_value) {
          const scrollInfo = this.cminstance.getScrollInfo();
          this.cminstance.setValue(newVal);
          this.content = newVal;
          this.cminstance.scrollTo(scrollInfo.left, scrollInfo.top)
        }
        this.unseenLineMarkers()
      },
      unseenLineMarkers() {
        if (this.unseenLines !== undefined && this.marker !== undefined) {
          this.unseenLines.forEach(line => {
            const info = this.cminstance.lineInfo(line);
            this.cminstance.setGutterMarker(line, 'breakpoints', info.gutterMarkers ? null : this.marker())
          })
        }
      },
      switchMerge() {
        // Save current values
        const history = this.cminstance.doc.history;
        const cleanGeneration = this.cminstance.doc.cleanGeneration;
        this.options.value = this.cminstance.getValue();

        this.destroy();
        this.initialize();

        // Restore values
        this.cminstance.doc.history = history;
        this.cminstance.doc.cleanGeneration = cleanGeneration
      }
    },

  }
</script>
<style lang="scss">
  @import "../../../scss/base";
  @import "../../../scss/components/vscode-theme-dark_plus";
  .code-hq {
    //font-size: 16px;
    overflow: auto;
  }
  .code_full-view .CodeMirror {
    height: 100%;
  }
  .CodeMirror {
    height: 100%;
  }
  .code-row_error {
    border: 1px solid $col-warning;
    border-left-width: 0;
    border-right-width: 0;
    &:first-child {
      border-left-width: 1px;
    }
    &:last-child {
      border-right-width: 1px;
    }
  }
</style>
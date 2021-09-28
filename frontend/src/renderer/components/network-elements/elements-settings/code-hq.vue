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
  // import 'codemirror/mode/gfm/gfm.js'
  // theme css
  // import 'codemirror/lib/codemirror.css'
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
  import 'codemirror/addon/scroll/simplescrollbars.js'

  export default {
    name: 'codeHq',
    props: {
      code: String,
      value: String,
      marker: Function,
      unseenLines: Array,
      name:             {type: String,   default: 'code-hq'},
      placeholder:      {type: String,   default: ''},
      merge:            {type: Boolean,  default: false },
      // options:   {type: Object,   default: () => ({})},
      autofocus:        {type: Boolean,  default: true },
      mode:             {type: String,   default: 'text/x-python' },
      lineNumbers:      {type: Boolean,  default: true },
      styleActiveLine:  {type: Boolean,  default: true },
      events:           {type: Array,    default: () => ([])},
      globalOptions:    {type: Object,   default: () => ({})},
      globalEvents:     {type: Array,    default: () => ([])},
      maxWidth:         {type: String,   default: '' },
      readOnly:         {type: Boolean,  default: false },

      errorRow: {type: [Number, String] }
    },
    mounted() {
      this.initialize();
      this.$nextTick(() => {

        const elements = document.querySelectorAll('.code-hq');
        for (const el of elements) {
          el.style.maxWidth = this.maxWidth;
        }
        
        this.cminstance.refresh();

        if(this.errorRowNumber) {
          this.cminstance.markText(
            { line: this.errorRowNumber - 1,  ch: 0 },
            { line: this.errorRowNumber,      ch: 0 },
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
          // autofocus: true,
          historyEventDelay: 100,
          tabSize: 4,
          // styleActiveLine: false,
          // lineNumbers: true,
          line: true,
          // mode: 'text/x-python',
          theme: "monokai",
          scrollbarStyle: 'overlay',
          readOnly: false
        }
      }
    },
    computed: {
      errorRowNumber() {
        return +this.errorRow

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
        this.options.autofocus = this.autofocus;
        this.options.mode = this.mode;
        this.options.lineNumbers = this.lineNumbers;
        this.options.styleActiveLine = this.styleActiveLine;
        this.options.readOnly = this.readOnly;

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

        this.cminstance.on('keydown', (cm, event) => {
          if (event.code === 'KeyS' && (event.ctrlKey || event.metaKey)) {
            event.preventDefault();
            event.stopPropagation();
            this.$emit('save-shortcut', this.content);
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
  
  @import "../../../scss/components/vscode-theme-dark_plus";
  @import "~codemirror/lib/codemirror.css";
  
  .code-hq {
    max-width: calc(50vw - #{$w-sidebar} + 123px);
  }
  .popup_body--show-code {
    .code-hq  {
      max-width: none;
    }
  }
  
  .code-hq {
    //font-size: 16px;
    overflow: auto;
    * {
      -webkit-user-select: initial;
      -moz-user-select: initial;
      -ms-user-select: initial;
      user-select: initial;
    }
  }
  .code_full-view .CodeMirror {
    height: 100%;
  }
  .CodeMirror {
    height: 100%;
    // text-align: left;
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


  .CodeMirror-gutters {
    left: -38px !important;
  }
  .CodeMirror-gutter-wrapper {
    left: -38px !important;
  }

  // scroll bar style

  .CodeMirror-simplescroll-horizontal div, .CodeMirror-simplescroll-vertical div {
    position: absolute;
    background: #ccc;
    -moz-box-sizing: border-box;
    box-sizing: border-box;
    border: 1px solid #bbb;
    border-radius: 2px;
  }

  .CodeMirror-simplescroll-horizontal, .CodeMirror-simplescroll-vertical {
    position: absolute;
    z-index: 6;
    background: #eee;
  }

  .CodeMirror-simplescroll-horizontal {
    bottom: 0; left: 0;
    height: 8px;
  }
  .CodeMirror-simplescroll-horizontal div {
    bottom: 0;
    height: 100%;
  }

  .CodeMirror-simplescroll-vertical {
    right: 0; top: 0;
    width: 8px;
  }
  .CodeMirror-simplescroll-vertical div {
    right: 0;
    width: 100%;
  }

  .CodeMirror-overlayscroll .CodeMirror-scrollbar-filler, .CodeMirror-overlayscroll .CodeMirror-gutter-filler {
    display: none;
    background: #1E1E1E;
  }

  .CodeMirror-overlayscroll-horizontal div, .CodeMirror-overlayscroll-vertical div {
    position: absolute;
    background: rgba($bg-scroll, .5);
    border-radius: 3px;
    /*transition: 0.3s;*/
  }

  .CodeMirror-overlayscroll-horizontal div:hover, .CodeMirror-overlayscroll-vertical div:hover {
    position: absolute;
    background: rgba($bg-scroll, 1);
    border-radius: 3px;
  }


  .CodeMirror-overlayscroll-horizontal, .CodeMirror-overlayscroll-vertical {
    position: absolute;
    z-index: 6;
  }

  .CodeMirror-overlayscroll-horizontal {
    bottom: 0; left: 0;
    height: 6px;
  }
  .CodeMirror-overlayscroll-horizontal div {
    bottom: 0;
    height: 100%;
  }

  .CodeMirror-overlayscroll-vertical {
    right: 0; top: 0;
    width: 6px;
  }
  .CodeMirror-overlayscroll-vertical div {
    right: 0;
    width: 100%;
  }

</style>

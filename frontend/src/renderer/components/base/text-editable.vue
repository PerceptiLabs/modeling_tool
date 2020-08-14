<template lang="pug">
  .editable-field(
    @dblclick="openEditMode"
    :class="styleType"
    )
    span.editable-field_title(:class="{textBackground: editMode}" ) {{ inputText }}
    .editable-field_input-wrap
      input.editable-field_input(type="text"
        v-show="editMode"
        v-model="inputText"
        @blur="closeEditMode"
        @keyup.enter="closeEditMode"
        ref="titleInput"
        )

</template>

<script>

  import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';

export default {
  name: "TextEditable",
  mixins: [mixinFocus],
  data() {
    return {
      editMode: false,
      inputText: this.textTitle
    }
  },
  props: {
    textTitle: {
      type: String,
      default: ''
    },
    styleType: {
      type: Array,
      default: function () {
        return [];
      }
    }
  },
  computed: {
    network() {
      return this.$store.getters['mod_workspace/GET_currentNetworkElementList']
    },
    setElementName() {
      return this.$store.getters['mod_workspace/SET_elementName']
    }
  },
  watch: {
    textTitle(newText) {
      this.inputText = newText;
    }
  },
  methods: {
    openEditMode() {
      this.setIsSettingInputFocused(true);
      this.$store.dispatch('mod_events/SET_enableCustomHotKey', false);
      this.editMode = true;
      setTimeout( ()=> {
          this.$refs.titleInput.focus()
        }, 100
      )
    },
    closeEditMode() {
      this.editMode = false;
      this.setIsSettingInputFocused(false);
      if(!this.inputText) this.inputText = this.textTitle;
      this.$emit('change-title', this.inputText);
      this.$store.dispatch('mod_events/SET_enableCustomHotKey', true);
    }
  }
}
</script>

<style lang="scss" scoped>
  .editable-field {
    display: inline-block;
    position: relative;
    cursor: pointer;
    min-width: 2em;
    min-height: 1em;
    &.network-view {
      input {
        background: transparent;
      }
      .textBackground {
        color: transparent;
      }
    }
  }

  .editable-field_input-wrap {
    position: absolute;
    top: 50%;
    right: -.5rem;
    left: -.5rem;
    transform: translateY(-50%);
    input {
      width: 100%;
      height: auto;
      padding: .25rem .5rem;
    }
  }
  
  
</style>

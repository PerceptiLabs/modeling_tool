<template lang="pug">
  div.input-wrapper
    div.input-container(
      :class="{'is-editable': !element.inputs[inputId].isDefault}"
       v-for="(input, inputId) in element.inputs"
       @dblclick="openInputEdit(inputId)"
       @contextmenu.stop.prevent="openContextMenu(inputId)"
    ) 
      span.input-name(
        v-if="!(inputEditId === inputId)"
      ) {{input.name}}
      input.setting-input-edit(
        v-if="isInputEditOpen && inputId == inputEditId"
        type="text"
        v-model="inputValue"
        @keyup.enter="saveInputName()"
      )
      div.circle-dot(
        :data-input-circle-dot-id="inputId"
        :data-input-layer-id="element.layerId"
      )
      div.input-dot(
        :data-input-dot-id="inputId"
        :data-input-layer-id="element.layerId"
      )
      div.input-context(
        v-if="isContextOpen && inputId === contextOpenedId"
      )
        button.input-context-button(@click.stop.prevent="addInput()") New input
        button.input-context-button(
          @click.stop.prevent="deleteInput()"
          v-if="!isLastVariable(element.inputs) && !element.inputs[contextOpenedId].isDefault"
          ) Delete input
</template>
<script>
import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
import baseNetPaintArrows from '@/core/mixins/base-net-paint-arrows.js';
export default {
  name: 'SettingInputs',
  mixins: [mixinFocus, baseNetPaintArrows],
  data() {
    return {
      isInputEditOpen: false,
      inputEditId: null,
      inputValue: '',
      isContextOpen: false,
      contextOpenedId: null,
    }
  },
  props:{
    element: {
      default: {},
      type: Object,
    }
  },
  methods: {
    openInputEdit(inputId){
      if(this.element.inputs[inputId].isDefault) {
        return;
      }
      this.inputValue = this.element.inputs[inputId].name;
      this.isInputEditOpen = true;
      this.inputEditId = inputId;
      this.setIsSettingInputFocused(true); // for prevent deleting the component when keydown backspace
    },
    closeInputEdit(){
      this.inputValue = '';
      this.isInputEditOpen = false;
      this.inputEditId = null;
      this.setIsSettingInputFocused(false);
    },
    saveInputName() {
      // save input value to stored
      this.$store.dispatch('mod_workspace/EDIT_inputVariableValueAction', {
        layerId: this.element.layerId,
        inputVariableId: this.inputEditId,
        value: this.inputValue,
      });
      this.closeInputEdit();
    },
    openContextMenu(inputId) {
      this.isContextOpen = true;
      this.contextOpenedId = inputId;
      // add event of click outside to close context
      document.addEventListener('click', this.onClickOutsideContextMenu);
    },
    closeContextMenu() {
      this.isContextOpen = false;
      this.contextOpenedId = null;
      document.removeEventListener('click', this.onClickOutsideContextMenu);
    },
    onClickOutsideContextMenu(ev){
      if(!this.elementOrAncestorHasClass(ev.target, 'input-container')) {
        this.closeContextMenu();
      }
    },
    elementOrAncestorHasClass(element, className) {
      if (!element || element.length === 0) {
        return false;
      }
      var parent = element;
      do {
        if (parent === document) {
          break;
        }
        if (parent.className.indexOf(className) >= 0) {
          return true;
        }
      } while (parent = parent.parentNode);
      return false;
    },
    isLastVariable(obj) {
      return Object.values(obj).length === 1;
    },
    addInput(){
      this.$store.commit('mod_workspace/ADD_inputVariableMutation', {
        layerId: this.element.layerId,
      });
      this.closeContextMenu();
    },
    deleteInput(){
      this.$store.dispatch('mod_workspace/DELETE_inputVariableAction', {
        layerId: this.element.layerId,
        inputVariableId: this.contextOpenedId,
      });
      this.closeContextMenu();
    },
  },
}
</script>
<style lang="scss" scoped>

.input-wrapper {
  width: 66px;
  //  *** For Training component with are bigger to fit input names ***
  .el-type-Training & {
    width: 75px;
  }
}
.input-name {
  display: block;
  overflow: hidden;
}
.input-container {
  margin: 4px 0 4px 22px;
  position: relative;
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 600;
  font-size: 10px;
  line-height: 22px;
  color: theme-var($neutral-8);

  // color: #FFFFFF;
  padding: 0 2px;
  &.is-editable {
    // background: rgba(54, 62, 81, 0.4);
    border: 1px solid #3F4C70;
    box-sizing: border-box;
    border-radius: 1px;
  }
}
.input-dot {
  position: absolute;
  left: -21px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  background-color: transparent;
  border-radius: 50%;

  &:hover {
    background: rgba(0, 0, 0, 0.3)
  }
}
.circle-dot {
  width: 5px;
  height: 5px;
  border: 1px solid $color-6;
  border-radius: 50%;
  position: absolute;
  left: -13px;
  top: 50%;
  transform: translateY(-50%);

  &.connect {
    background: #6185EE;
  }
}
.setting-input-edit {
  height: 17px;
  padding: 2px;
}
.input-context {
  position: absolute;
  z-index: 200;
  width: 70px;
  background: #0B0D13;
  border: 1px solid #363E51;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3);
  border-radius: 2px;
  padding: 3px 0;
}
.input-context-button {
  background: transparent;
  color: #fff;
  font-family: Nunito Sans;
  font-size: 9px;
  line-height: 12px;
  &::hover {
    background: rgba(97, 133, 238, 0.75);
  }
}
</style>
<template lang="pug">
  div
    div.output-container(
      v-for="(output, outputId) in element.outputs"
      @contextmenu.stop.prevent="openContextMenu(outputId)"
      @click.stop.prevent="openVariablesList(outputId)"
      :data-output-id="outputId"
    ) {{output.name}}
      div.circle-dot(
        :data-output-circle-dot-id="outputId"
        :data-output-layer-id="element.layerId"
      )
        .icon.icon-left-arrow-dot-line(
          :class="{'hover': hoverHandle === true}"
        )      
      div.output-dot(
        :data-output-dot-id="outputId"
        :data-output-layer-id="element.layerId"
        @mousedown.stop.prevent="startPreviewArrow"
        @mouseover="handlehover"
        @mouseleave="handleleave"
      )

      div.variable-list(
        v-if="isVarableListOpen && outputId === variableListId"
      )
        button.variable-list-button(
          v-for="(variable) in outputsVariables"
          @click.stop.prevent="assignVariable(variable)"
        ) {{variable}}
      
      
      div.output-context(
        v-if="isContextOpen && outputId === contextOpenedId"
      )
        button.output-context-button(@click.stop.prevent="addOutput()") New output
        button.output-context-button(
          @click.stop.prevent="deleteOutput()"
          v-if="!isLastVariable(element.outputs)"
          ) Delete output
        
</template>
<script>
import { mapActions } from 'vuex';
import baseNetPaintArrows from '@/core/mixins/base-net-paint-arrows.js';
export default {
  name: 'SettingOutputs',
  mixins: [baseNetPaintArrows],
  data() {
    return {
      isVarableListOpen: false,
      variableListId: null,
      isContextOpen: false,
      contextOpenedId: null,
      hoverHandle: false,
    }
  },
  props: {
    element: {
      default: () => {},
      type: Object,
    },
    outputsVariables: {
      default: () => [],
      type: Array,
    }
  },
  methods: {
    ...mapActions({
      setNetMode:               'mod_workspace/SET_netMode',
      api_getVariableList:      'mod_api/API_getPreviewVariableList',
    }),
    openContextMenu(outputId) {
      this.isContextOpen = true;
      this.contextOpenedId = outputId;
      // add event of click outside to close context
      document.addEventListener('click', this.onClickOutside);
    },
    closeContextMenu() {
      this.isContextOpen = false;
      this.contextOpenedId = null;
      document.removeEventListener('click', this.onClickOutside);
    },
    onClickOutside(ev) {
      if(!this.elementOrAncestorHasClass(ev.target, 'output-container')) {
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
    addOutput() {
      // chose automatically nex variable from variables provided in 'outputsVariables'
      // this.outoputs.push('none');
      this.$store.commit('mod_workspace/ADD_outputVariableMutation', {
        layerId: this.element.layerId,
      });
      this.closeContextMenu();

    },
    deleteOutput() {
      if(this.isLastVariable(this.element.outputs)) {
        return;
      }
      // @todo alert that last variable can't be removed
      this.$store.dispatch('mod_workspace/DELETE_outputVariableAction', {
        layerId: this.element.layerId,
        outputVariableId: this.contextOpenedId,
      })
      .then((layerIdsWithReferene) => {
        if(layerIdsWithReferene.length > 0) {
          for(let ix in layerIdsWithReferene) {
            this.$store.dispatch('mod_api/API_getBatchPreviewSampleForElementDescendants', layerIdsWithReferene[ix]);
          }
       }
      })
      // this.outoputs.splice(this.contextOpenedId, 1);
      this.closeContextMenu();
    },
    isLastVariable(obj) {
      return Object.values(obj).length === 1;
    },
    openVariablesList(outputId){
      this.isVarableListOpen = true;
      this.variableListId = outputId;
      this.getVariableList();
      document.addEventListener('click', this.onClickOutsideVariableMenu);
    },
    closeVariableList(){
      this.isVarableListOpen = false;
      this.variableListId = null;
      document.removeEventListener('click', this.onClickOutsideVariableMenu);
    },
    onClickOutsideVariableMenu(ev){
      if(!this.elementOrAncestorHasClass(ev.target, 'variable-list')){
        this.closeVariableList();
      }
    },
    assignVariable(variableName){
      // this.outoputs[this.variableListId] = variableName;
      this.$store.dispatch('mod_workspace/SET_outputVariableAction', {
        layerId: this.element.layerId,
        outputVariableId: this.variableListId,
        variableName: variableName,
      })
      this.$store.dispatch('mod_api/API_getBatchPreviewSampleForElementDescendants', this.element.layerId);
      this.closeVariableList();
    },
    startPreviewArrow(ev) {
      this.$parent.$parent.startArrowPaint(ev);
    },
    handlehover() {
      this.hoverHandle=true;
    },
    handleleave() {
      this.hoverHandle=false;
    },
    getVariableList() {
      this.$store.dispatch('mod_api/API_getPreviewVariableList', this.element.layerId)
        .then((data)=> {
          this.$store.commit('mod_workspace/SET_previewVariable', {
            layerId: this.element.layerId,
            previewVariableName: data.VariableName,
          });
          this.$store.commit('mod_workspace/SET_previewVariableList', {
            layerId: this.element.layerId,
            previewVariableList: data.VariableList,
          });

        })
    },
  }

}
</script>
<style lang="scss" scoped>
.output-container {
  position: relative;
  width: 55px;
  padding: 4px;
  border-radius: 1px;
  border: 1px solid rgba(97, 133, 238, 0.4);
  background: #131B30;
  margin: 4px 19px 4px 0;
}
.output-dot {
  position: absolute;
  right: -20px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  background-color: transparent;
  border-radius: 50%;

  &:hover {
    background-color: rgba(255, 255, 255, 0.3);
  }

}

.circle-dot {
  width: 5px;
  height: 5px;
  border: 1px solid white;
  border-radius: 50%;
  position: absolute;
  right: -13px;
  top: 50%;
  transform: translateY(-50%);

  &.connect {
    background: #B6C7FB;
  }
}

.icon-left-arrow-dot-line {
  position: absolute;
  top: -2.5px;
  left: 1px;
  display: none;
  animation: slide1 1s ease-in-out infinite;

  &.hover {
    display: block;
    color: #B6C7FB;
  }
}

@keyframes slide1 {
  0%,
  100% {
    transform: translate(0, 0);
  }

  50% {
    transform: translate(4px, 0);
  }
}

.output-context {
  position: absolute;
  z-index: 200;
  width: 70px;
  background: #0B0D13;
  border: 1px solid #363E51;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3);
  border-radius: 2px;
  padding: 3px 0;
}
.output-context-button {
  background: transparent;
  color: #fff;
  font-family: Nunito Sans;
  font-size: 9px;
  line-height: 12px;
  &::hover {
    background: rgba(97, 133, 238, 0.75);
  }
}
.variable-list {
  position: absolute;
  z-index: 200;
  background: #0B0D13;
  border: 1px solid #363E51;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3);
  border-radius: 2px;
  padding: 3px 0;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
.variable-list-button {
  display: block;
  width: 100%;
  text-align: left;
  background: transparent;
  color: #fff;
  font-family: Nunito Sans;
  font-size: 9px;
  line-height: 12px;
  &:hover {
    background: rgba(97, 133, 238, 0.75);
  }
}
</style>
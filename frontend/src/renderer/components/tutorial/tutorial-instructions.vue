<template lang="pug">
.tutorial-instruction-box
  slot

  .tutorial-instruction-box_list-area(v-if="isShowInstructions" @mousedown="dragElement($event)")
    header.list-area_header
      div
        button.header_close-instructions.i.icon.icon-app-close(@click="switchTutorialMode")
        //span.header_title title_q
      .header_arrows-top(:class="{'list-hide': !isMaximize}" @click="minimizeList")
        i.icon.icon-shevron
        i.icon.icon-shevron

    .list-area-box(v-show="isMaximize")
      p.list-area_title {{interective[activeStep].title}}
      ul.list-area_list
        .list-element.list-element--status(
          v-for="(point, index) in points"
          :key="index"
          :class="[point.class_style, {'active': point.status === 'active', 'done': point.status === 'done'}]"
        )
          .element-text(v-html="point.content")
          .list-element_static
            .static_info.list-element--status(
              v-for="(info, index) in point.static_info"
              v-html="info.content"
              :key="index"
              :class="[{'done': info.status === 'done'}]"
            )

      footer.list-area_footer
        button.footer_all-tutorials-btn
          i.icon.icon-shevron-right
          span All tutorials
        .curent-steps(v-if="activeStep !== 'first_instructions'") {{stepCount}}/{{stepsLength}}
        div
          //button.footer_btn(v-if="stepCount > 0" @click="changeStep('back')") Back
          button.footer_btn(
            v-if="isFirstStep"
            @click="startTutorial('next')"
            ) Next
          button#tutorial_next_button.footer_btn(
            v-else-if="activeAction.next && !allPointsIsDone"
            @click="pointActivate({way: 'next', validation: activeAction.id})"
            ) Next
          button#tutorial_next_button.footer_btn(
            v-else-if="stepCount !== stepsLength"
            @click="changeStep('next')" :disabled="disabledNext"
            ) Next
          button.footer_btn(
            v-else-if="stepCount === stepsLength"
            @click="endTutorial()"
            ) End
</template>
<script>
import { mapGetters, mapMutations, mapActions } from 'vuex';
export default {
  name: 'TutorialInstructions',
  data() {
    return {
      count: 0,
      isMaximize: true
    }
  },
  watch: {
    eventResize() {
      this.tooltipReposition();
    },
    isTutorialMode(isTutorialMode) {
      let layersbar = document.querySelector('.page_layersbar');
      let svg = document.querySelector('.svg-arrow');
      if(isTutorialMode) {                                              //hide tooltip for elements from toolbar when these elements are hidden
        svg.addEventListener('click', this.hideTooltip);
        layersbar.addEventListener('click', this.showHideTooltip, true);
      }
      else {
        svg.removeEventListener('click', this.hideTooltip);
        layersbar.removeEventListener('click', this.showHideTooltip);
      }
    },
    statisticsIsOpen(newVal) {
      if(newVal) this.pointActivate({way: null, validation: this.activePoint.actions[0].id})
    }
  },
  computed: {
    ...mapGetters({
      activeStep:                 'mod_tutorials/getActiveStep',
      points:                     'mod_tutorials/getPoints',
      interective:                'mod_tutorials/getIterective',
      isTutorialMode:             'mod_tutorials/getIstutorialMode',
      stepCount:                  'mod_tutorials/getActiveStepMainTutorial',
      allPointsIsDone:            'mod_tutorials/getAllPointsIsDone',
      activePoint:                'mod_tutorials/getActivePoint',
      activeAction:               'mod_tutorials/getActiveAction',
      isShowInstructions:         'mod_tutorials/getShowMainTutorialInstruction',
      currentNetworkElementList:  'mod_workspace/GET_currentNetworkElementList',
      statisticsIsOpen:           'mod_workspace/GET_statisticsIsOpen',
    }),
    currentNetwork() {
      return this.$store.state.mod_workspace.currentNetwork
    },
    eventResize() {
      return this.$store.state.mod_events.eventResize
    },
    stepsLength() {
      return Object.keys(this.interective).length - 1
    },
    isFirstStep() {
      return this.interective[this.activeStep].points[0].status === 'first'
    },
    disabledNext() {
      return this.activeStep === 'run_training' || !this.allPointsIsDone
    },
    workspaceContent() {
      return this.$store.state.mod_workspace.workspaceContent
    }
  },
  methods: {
    ...mapMutations({
      setActiveStep:              'mod_tutorials/SET_activeStepMainTutorial',
      setTutorialIstarted:        'mod_tutorials/SET_mainTutorialIsStarted',
      setTutorialMode:            'mod_tutorials/SET_isTutorialMode',
      goToFirstStep:              'mod_tutorials/SET_activeActionMainTutorial',
      setShowInstructions:        'mod_tutorials/SET_showMainTutorialInstruction',
      setInteractiveInfo:         'mod_tutorials/SET_interactiveInfo',
      deleteNetwork:              'mod_workspace/DELETE_network'
    }),
    ...mapActions({
      pointActivate:              'mod_tutorials/pointActivate',
      pointsDeactivate:           'mod_tutorials/pointsDeactivate',
      resetTutorial:              'mod_tutorials/resetTutorial',
      lockElements:               'mod_tutorials/lockElements',
      unlockAllElements:          'mod_tutorials/unlockAllElements',
      tooltipReposition:          'mod_tutorials/tooltipReposition',
      offTutorial:                'mod_tutorials/offTutorial',
      showHideTooltip:            'mod_tutorials/showHideTooltip',
      hideTooltip:                'mod_tutorials/hideTooltip',
      onTutorial:                 'mod_tutorials/onTutorial',
      setNetworkCoreStatus:       'mod_workspace/SET_statusNetworkCoreStatus',
      addNetwork:                 'mod_workspace/ADD_network',
      popupInfo:                  'globalView/GP_infoPopup',
      trackerTutorialStart:       'mod_tracker/EVENT_tutorialModeStart',
      trackerTutorialFinished:    'mod_tracker/EVENT_tutorialModeFinished'
    }),
    changeStep(way) {
      if(way === 'next') {
        this.setActiveStep(way);
        this.pointActivate({way: null, validation: this.activePoint.actions[0].id})
      }
    },
    startTutorial(way) {
      //if(this.currentNetworkElementList) this.addNetwork();
      this.setTutorialIstarted(true);
      this.setActiveStep(way);
      this.pointActivate({way: null, validation: this.activePoint.actions[0].id});
      this.trackerTutorialStart();
    },
    endTutorial() {
      this.setNetworkCoreStatus(false);
      this.popupInfo(`Congratulations, you have successfully completed the Tutorial!
                      If you wish to save the model you created, can do so from the File menu in the top left.
                      Or you can export it by clicking on the tab "Export" in the right menu.`);
      this.switchTutorialMode();
      this.trackerTutorialFinished();
    },
    switchTutorialMode() {
      if(this.isTutorialMode) {
        this.offTutorial();
      } else {
        this.onTutorial(this);
        this.isMaximize = true;
        if(this.currentNetworkElementList) this.addNetwork();
      }
    },

    minimizeList() {
      this.isMaximize = !this.isMaximize;
    },
    dragElement(event) {
      let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
      let elementDrag = (docEvent) => {
        event.preventDefault();
        pos1 = pos3 - docEvent.clientX;
        pos2 = pos4 - docEvent.clientY;
        pos3 = docEvent.clientX;
        pos4 = docEvent.clientY;
        element.style.top = (element.offsetTop - pos2) + "px";
        element.style.left = (element.offsetLeft - pos1) + "px";
      };

      let closeDragElement = () => {
        document.removeEventListener('mouseup', closeDragElement);
        document.removeEventListener('mousemove', elementDrag);
        element.style.cursor = '';
        if (!this.disabledNext || this.activeAction.next && !this.allPointsIsDone) {
          this.tooltipReposition(true);
        }
      };
      const element = event.currentTarget;
      event.preventDefault();
      pos3 = event.clientX;
      pos4 = event.clientY;
      element.style.cursor = 'grabbing';
      document.addEventListener('mouseup', closeDragElement);
      document.addEventListener('mousemove', elementDrag);
    }
  }
}

</script>
<style lang="scss">
  @import "../../scss/base";
  @import "../../scss/directives/tooltip";
  $color-text-instructions:#AEAEAE;
  $color-schematic-element: #3185aa;
  $title-padding: 0 2.1rem;

  .btn--dark-blue-rev {
    position: relative;
    z-index: 1;
  }
  .tutorial-instruction-box {
    position: relative;
  }
  .tutorial-instruction-box_list-area {
    position: absolute;
    z-index: 13;
    background: $col-txt2;
    width: 32rem;
    top: 90%;
    right: 0;
    color: $white;
    border-radius: 5px;
    overflow: hidden;
    box-shadow: $box-shad;
    cursor: move;
  }
  .list-area_header {
    background: $bg-workspace;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 2.6rem;
    margin-bottom: 1rem;
  }
  .header_close-instructions {
    background: none;
    border: 1px solid $color-text-instructions;
    color: $color-text-instructions;
    border-radius: 20rem;
    font-size: 0.9rem;
    padding: 0.1rem;
    margin-left: 0.5rem;
  }
  .header_title {
    font-size: 1.4rem;
    margin-left: 1rem;
    color: $color-text-instructions;
  }
  .header_arrows-top {
    transform: rotate(-180deg);
    color: $col-txt;
    background: $col-txt2;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    padding: 0 1.2rem;
    cursor: pointer;
    &.list-hide {
      transform: rotate(0);
    }
    .icon{
      font-size: 1.3rem;
      position: relative;
      &:first-child {
        top: 0.4rem;
      }
      &:last-child {
        top: -0.4rem;
      }
    }
  }
  .list-area_title {
    font-size: 1.4rem;
    padding: 0 2.5rem;
    font-weight: 500;
  }
  .list-area_list {
    height: 25rem;
    overflow: scroll;
  }
  .list-element--status {
    position: relative;
    &:before {
      position: absolute;
      top: 0;
      left: 2.6rem;
      font-family: "icomoon";
      speak: none;
    }
    &.active:before {
      content: "\e901";
      left: 1.8rem;
    }
    &.done:before {
      content: "\e968";
      left: 2rem;
    }
  }
  .list-element--status.static_info {
    position: relative;
    &.done:before {
      left: -2rem;
    }
  }
  .list-element {
    margin-bottom: 0.5rem;
    font-size: 1.6rem;
    position: relative;
    padding: 0 2.5rem 0 3.5rem;
   
    &.list_title{
      font-weight: 700;
      font-size: 1.4rem;
      padding: $title-padding;
    }
    &.list_subtitle {
      padding: $title-padding;
      &:before {
        position: static;
        margin-right: 0.5rem;
      }
    }
    .marker {
      color: #3bc5ff;
      font-weight: 700;
      display: inline;
    }
    & .text-block{
      margin-bottom: 1rem;
    }
    p {
        margin-bottom: 0.2rem;
    }
  }
  .list-element_static {
    padding: 0 1.5rem
  }
  .element-text {
    display: inline;
    margin-bottom: 1rem
  }
  .static_info {
    margin-bottom: 0.5rem;
    &:first-child {
      margin-top: 1rem
    }
  }
  .list-area_footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding: 0 1rem;
    button {
      background: none;
    }
  }
  .footer_all-tutorials-btn {
    display: flex;
    align-items: center;
    color: $color-text-instructions;
    padding: 0;
    opacity: 0;
    .icon {
      transform: rotate(-180deg);
      display: inline-block;
      margin-right: 0.5rem;
    }
    font-size: 1.2rem;
  }
  .footer_btn {
    font-size: 1.2rem;
    border: 1px solid $login-blue;
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    margin-right: 1rem;
    &:last-child {
      margin-right: 0; 
    }
    &[disabled] {
      border: 1px solid $color-text-instructions;
      color: $color-text-instructions;
    }
  }
  .curent-steps {
    font-size: 1.2rem;
    color: $color-text-instructions;
  }
.schematic--square {
  width: 7.5rem;
  height: 7.5rem;
  border-radius: 5px;
  border: 2px dotted $color-schematic-element;
  position: absolute;
}
.tutorial_target-border {
  position: relative;
  &:after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    border: 2px solid #3BC5FF;
    pointer-events: none;
  }
}
.lock-area {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 5;
  width: 100%;
  height: 100%;
}
.unlock-element {
  z-index: 6;
  position: relative;
}
</style>

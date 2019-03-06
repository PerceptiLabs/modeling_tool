<template lang="pug">
.tutorial-instruction-box(v-if="isTutorialMode") 
    button.btn.btn--dark-blue-rev.green-status(type="button"
      @click="showInstructions"
    )
      span Tutorial Mode
      i.icon.icon-ellipse
    
    .tutorial-instruction-box_list-area(v-if="isShowInstructions")
      header.list-area_header
        div
          button.header_close-instructions.i.icon.icon-appClose(@click="showInstructions")
          span.header_title title_q
        .header_arrows-top
          i.icon.icon-shevron
          i.icon.icon-shevron
      
      p.list-area_title {{interective[activeStep].title}}
      ul.list-area_list
        .list-element(
          v-for="(point, index) in points"
          v-html="point.content"
          :key="index"
          :class="[point.class_style, {'active': point.pointStatus === 'active', 'done': point.pointStatus === 'done'}]"
        )
          
      footer.list-area_footer
        button.footer_all-tutorials-btn
          i.icon.icon-shevron-right
          span All tutorials
        .curent-steps(v-if="activeStep !== 'first_instructions'") {{stepCount}}/{{stepsLength}}
        div
          //button.footer_btn(v-if="stepCount > 0" @click="changeStep('back')") Back 
          button.footer_btn(v-if="isFirstStep" @click="startTutorial('next')") Next
          button.footer_btn(v-else @click="changeStep('next')" :disabled="!allPointsIsDone") Next
</template>
<script>
import { mapGetters, mapMutations, mapActions } from 'vuex';
export default {
  name: 'TutorialInstructions',
  data() {
    return {
      isShowInstructions: false,
      count: 0
    }
  },
  computed: {
    ...mapGetters({
      activeStep:       'mod_tutorials/getActiveStep',
      points:           'mod_tutorials/getPoints',
      interective:      'mod_tutorials/getIterective',
      isTutorialMode:   'mod_tutorials/getIstutorialMode',
      stepCount:        'mod_tutorials/getActiveStepMainTutorial',
      allPointsIsDone:  'mod_tutorials/getAllPointsIsDone',
      activePoint:      'mod_tutorials/getActivePoint'
    }),
    stepsLength() {
      return Object.keys(this.interective).length - 1
    },
    isFirstStep() {
      return this.interective[this.activeStep].points[0].pointStatus === 'first'
    }
  },
  methods: {
    ...mapMutations({
      setActiveStep:        'mod_tutorials/SET_activeStepMainTutorial',
      setTootorialIstarted: 'mod_tutorials/SET_mainTutorialIsStarted',
      goToFirstStep:        'mod_tutorials/SET_activeActionMainTutorial'
    }),
    ...mapActions({
      pointActivate:    'mod_tutorials/pointActivate',
      pointsDeactivate: 'mod_tutorials/pointsDeactivate',
    }),
    showInstructions() {
      this.isShowInstructions =  !this.isShowInstructions
    },
    changeStep(way) {
      if(way === 'next') {
        this.setActiveStep(way)
        this.pointActivate({way: null, validation: this.activePoint.actions[0].id})
      }
    },
    startTutorial(way) {
      this.setTootorialIstarted(true)
      this.setActiveStep(way)
      this.pointActivate({way: null, validation: 'tutorial_data'})
    }
  }
}
</script>
<style lang="scss">
  @import "../../scss/base";
  $color-text-instructions:#AEAEAE;
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
    z-index: 1;
    background: $col-txt2;
    width: 24rem;
    top: 90%;
    right: 0;
    color: $white;
    border-radius: 5px;
    overflow: hidden;
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
    color: $col-txt;
    background: $col-txt2;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    padding: 0 1.2rem;
    .icon{
      font-size: 1.3rem;
      position: relative;
      transform: rotate(-90deg);
      &:first-child {
        top: 0.4rem;
      }
      &:last-child {
        top: -0.4rem;
      }
    }
  }
  .list-area_title {
    font-size: 1.2rem;
    padding: 0 2.5rem;
    font-weight: 500;
  }
  .list-area_list {
    height: 15rem;
    overflow: scroll;
  }
  .list-element {
    margin-bottom: 1.5rem;
    font-size: 1.2rem;
    position: relative;
    padding: 0 2.5rem 0 3.5rem;
    &:before {
      position: absolute;
      top: 0;
      left: 2.6rem;
      font-family: "icomoon";
      speak: none;
    }
    &.active:before {
      content: "\e901";
      left: 2rem;
    }
    &.done:before {
      content: "\e937";
      left: 2rem;
    }
    &.list_title{
      font-weight: 700;
      font-size: 1.2rem;
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
    font-size: 1.2;
    color: $color-text-instructions;
  }
.tooltip-tutorial {
  font-size: 1.2rem;
  font-weight: 400;
	color: $bg-workspace;
	position: absolute;
	z-index: 100;
	min-width: 3rem;
	max-width: 30rem;
	padding: .8rem .6rem;
	border-radius: 0.2rem;
	white-space: nowrap;
	background-color: #3BC5FF;
	box-shadow: $icon-shad;
	pointer-events: none;
	left: 120%;
	text-align: left;
	&:before {
		content: '';
		position: absolute;
		right: 100%;
    width: 0;
    height: 0;
    border-top: 6px solid transparent;
    border-right: 10px solid #3BC5FF;
    border-bottom: 6px solid transparent;
	}
}
.tutorial-relative{
  position: relative;
  overflow: visible;
}
button.btn--primary.tutorial-relative .tooltip-tutorial{
  top: 0;
}
</style>
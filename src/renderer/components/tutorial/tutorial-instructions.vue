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
          :class="[point.class_style, {'active': point.isActive}]"
        )
          
      footer.list-area_footer
        button.footer_all-tutorials-btn
          i.icon.icon-shevron-right
          span All tutorials
        .curent-steps(v-if="activeStep !== 'first_instructions'") {{stepCount}}/{{stepsLength}}
        div
          button.footer_btn(v-if="stepCount > 0" @click="changeStep('back')") Back
          button.footer_btn(v-if="stepCount < stepsLength" @click="changeStep('next')") Next
</template>
<script>
import { mapGetters, mapMutations } from 'vuex';
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
      activeStep:     'mod_tutorials/getActiveStep',
      points:         'mod_tutorials/getPoints',
      interective:    'mod_tutorials/getIterective',
      isTutorialMode: 'mod_tutorials/getIstutorialMode',
      stepCount:      'mod_tutorials/getActiveStepMainTutorial',
    }),
    stepsLength() {
      return Object.keys(this.interective).length - 1
    }
  },
  methods: {
    ...mapMutations({
      setActiveStep:    'mod_tutorials/SET_activeStepMainTutorial',
      setActivePoint:   'mod_tutorials/SET_pointActivate',
      setPointDone:     'mod_tutorials/SET_pointDone',
      setActiveAction:  'mod_tutorials/SET_activeAction'
    }),
    showInstructions() {
      this.isShowInstructions =  !this.isShowInstructions
    },
    changeStep(way) {
      if(way === 'next') {
        this.count++
        this.setActiveStep(this.count)
        this.pointActivate()
      } else {
          this.count--
          this.setActiveStep(this.count)
          this.pointsDeactivate()
      }
    },
    pointActivate() {
      this.pointsDeactivate()
      let actionsDoneCount = 0;
      
      for(let indexPoint = 0; indexPoint < this.points.length; indexPoint++ ) {
        let point = this.points[indexPoint]
        if(!point.done && !point.isActive) {
          this.setActivePoint({step: this.activeStep, point: indexPoint, isActive: true})
          
          for(let indexAction = 0; indexAction < point.actions.length; indexAction++) {
            let action = point.actions[indexAction]
            if(action.actionStatus === 'done') {
              actionsDoneCount++
              if(actionsDoneCount === point.actions.length) {
                
                break
              }
            }
            if(action.actionStatus === 'active') {
                this.setActiveAction({
                step: this.activeStep, 
                point: indexPoint, 
                action: indexAction, 
                actionStatus: 'done'
              })
            }
            if(action.actionStatus === 'disabled') {
              this.setActiveAction({
                step: this.activeStep, 
                point: indexPoint, 
                action: indexAction, 
                actionStatus: 'active'
              })
              break
            }
          }
          break
        }
      }
    },
    pointsDeactivate() {
      for(let index = 0; index < this.points.length; index++ ) {
        if(this.activeStep !== 'first_instructions') {
          this.setActivePoint({step: this.activeStep, point: index, isActive: false})
          this.setPointDone({step: this.activeStep, point: index, done: false})
        }
      } 
    }
  },
  mounted() {
    
  }
}
</script>
<style lang="scss">
  @import "../../scss/base";
  $color-text-instructions:#AEAEAE;
  $title-padding: 0 2.1rem;


  .btn--dark-blue-rev {
    position: relative;
    z-index: 2;
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
    padding: 0 2.5rem;
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
</style>
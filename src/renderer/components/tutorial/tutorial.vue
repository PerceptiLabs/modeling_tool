<template lang="pug">
  .tutorial-box
    
    .tutorial-box_modal-popup(
      v-for="(step, index) in firstTutorial" 
      key="index"
      v-if="activeSlide === index"
    )
      .modal-popup_eyes
        .eyes.eye-one
          .eye_pupil(:class="step.lookEyesClass")
        .eyes.eye-two
          .eye_pupil(:class="step.lookEyesClass")
      button.close-tutorial.i.icon.icon-empty
      .modal-popup_title {{step.title}}
      .modal-popup_info {{step.text}}
      .modal-popup_after-info
        img(:src="step.img" alt="step image" v-if="step.img")
        button.btn--crash-course(v-if="step.button") {{step.button}} 
        
      button.modal-popup_control.prev-button.i.icon.icon-player-play(@click="step.prevStepActive" v-show="activeSlide > 0")
      button.modal-popup_control.next-button.i.icon.icon-player-play(@click="step.nextStepActive" v-show="activeSlide < firstTutorial.length - 1")
      footer.modal-popup_footer
        button.footer_skip-button Skip intro

        ul.footer_all-slides-controls
          li.all-slides-controls_control(
            v-for="(control, index) in firstTutorial"
            :class="{'active': activeSlide === index}"
            @click="activeSlide = index"
          )
</template>
<script>
export default {
  name: 'Tutorial',
  data() {
    return {
      activeSlide: 0,
      firstTutorial: [
        {
          title: 'What is AI?',
          text: 'AI refers to a machine or a software program that simulates human intelligence to accomplish a certain task (often in a narrow area).',
          img: './static/imgs/tutorial/tutorial-1_step-1-icon.svg',
          lookEyesClass: 'look-bottom',
          prevStepActive: ()=> {this.prevStep()},
          nextStepActive: ()=> {this.nextStep()}
        },
        {
          title: 'How does it work?',
          text: 'AI learns to respond to information in a certain way, depending on what you train it for. It uses historical data and algorithms to generate a model that is able to make decisions and/or predictions.',
          img: './static/imgs/tutorial/tutorial-1_step-2-icon.svg',
          lookEyesClass: 'look-bottom',
          prevStepActive: ()=> {this.prevStep()},
          nextStepActive: ()=> {this.goToThreeStep()}
        },
        {
          title: 'Where do I begin?',
          text: 'The left toolbar contains all the operations you need to build your AI model. Fret not - we’ve coded the backend for you! All you have to do is drop your desired operations onto this workspace.',
          img: './static/imgs/tutorial/tutorial-1_step-3-icon.svg',
          lookEyesClass: 'look-left',
          prevStepActive: ()=> {this.backToTwoStep()},
          nextStepActive: ()=> {this.nextStep()}
        },
        {
          title: 'Customise with PerceptiLabs',
          text: 'PerceptiLabs allows you to customise everything from building your model to managing your workflow. On the right, get an overview of your project, customize your profile settings, and import/ export your favourite models.',
          img: './static/imgs/tutorial/tutorial-1_step-4-icon.svg',
          lookEyesClass: 'look-top-right',
          prevStepActive: ()=> {this.prevStep()},
          nextStepActive: ()=> {this.nextStep()}
        },
        {
          title: 'Don’t forget to ‘Run’',
          text: 'When you are satisfied with the neural network you have built on this workspace, be sure to hit the ‘Run’ button above to generate your AI model.',
          img: './static/imgs/tutorial/tutorial-1_step-5-icon.svg',
          lookEyesClass: 'look-top-left',
          prevStepActive: ()=> {this.prevStep()},
          nextStepActive: ()=> {this.nextStep()}
        },
        {
          title: 'Build your first neural network!',
          text: 'Following this introduction is a step-by-step guide on how to build a simple neural network. It creates an AI model for image classification, which programmes the computer to recognise and classify simple images. ',
          button: `Let's Try It`,
          lookEyesClass: 'look-close',
          prevStepActive: ()=> {this.prevStep()},
          nextStepActive: ()=> {this.nextStep()}
        }
      ]
    }
  },
  methods: {
    nextStep() {
      this.activeSlide++
    },
    prevStep() {
      this.activeSlide--
    },
    goToThreeStep() {
      this.nextStep();
      this.$store.commit('mod_tutorials/SET_leftToolBarActive', true)
    },
    backToTwoStep() {
      this.prevStep();
      this.$store.commit('mod_tutorials/SET_leftToolBarActive', false);
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "../../scss/base";
  $distance-control-btn: -6rem;
  $popup-bg-gradient:linear-gradient(to top, #212328, #252931);

  .tutorial-box {
    position: fixed;
    top: 0;
    left: 0;
    background: rgba(0, 0, 0, .5);
    width: 100%;
    height: 100%;
    z-index: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    background: rgba(35, 37, 42, 0.7);
  }
  .tutorial-box_modal-popup {
    border: 1px solid $col-primary;
    border-radius: 5px;
    padding: 6rem 3rem 2rem 3rem;
    position: relative;
    background: $popup-bg-gradient;
    width: 41rem;

    button.close-tutorial {
      color: $col-primary;
      position: absolute;
      font-size: 2rem;
      top: .4rem;
      left: .4rem;
      padding: 0;
      background: none;
    }
  }
  .modal-popup_eyes {
    display: flex;
    justify-content: center;
    position: absolute;
    width: 100%;
    left: 0;
    top: -2rem;
  }
  .eyes {
    border: 1px solid $col-primary;
    width: 4rem;
    height: 4rem;
    border-radius: 20rem;
    background: $popup-bg-gradient;
    margin-right: 2rem;
    position: relative;
    &:last-child {
      margin-right: 0rem;
    }
  }
  .eye_pupil {
    border: 1px solid $col-primary;
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 20rem;
    background: $bg-workspace;
    position: absolute;
    top: 0;
    left: 0;
    
    &.look-top {
      transform: translate(27%, 10%);
    }
    &.look-right {
      transform: translate(40%, 27%);
    }
    &.look-bottom {
      transform: translate(26%, 45%);
    }
    &.look-left {
      transform: translate(10%, 25%);
    }
    &.look-top-right {
      transform: translate(40%, 16%);
    }
    &.look-bottom-right {
      transform: translate(40%, 36%);
    }
    &.look-top-left {
      transform: translate(13%, 16%);
    }
    &.look-bottom-left {
      transform: translate(16%, 37%);
    }
    &.look-close {
      transform: translate(26%, 35%);
      border: none;
      border-top: 2px solid $col-primary;
      height: 3.7rem;
      background: none;
    }
  }
  .modal-popup_title {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 2rem;
  }
  .modal-popup_info {
    font-size: 1.4rem;
    margin-bottom: 2rem;
    line-height: 1.6rem;
  }
  .modal-popup_control {
    position: absolute;
    top: 50%;
    display: flex;
    justify-content: space-between;
    background: none;
    color: $col-primary;
    font-size: 5rem;
    transform: translate(0, -50%);
    cursor: pointer;

    &.prev-button {
      left: -6rem;
      transform: translate(0, -50%) rotate(-180deg);
    }
    &.next-button {
      right: -6rem;
    }
  }
  .modal-popup_after-info {
    text-align: center;
  }
  .modal-popup_footer {
    display: flex;
    flex-direction: column;
    margin: 3rem 0 0 0;
  }
  .footer_skip-button {
    color: $col-primary;
    border-bottom: 1px solid $col-primary;
    font-size: 1.1rem;
    padding: 0 0 0.3rem 0;
    margin-left: auto;
    background: none;
  }
  .footer_all-slides-controls {
    margin: auto;
    display: flex;
    width: 100%;
    justify-content: center;
  }
  .all-slides-controls_control {
    width:  .7rem;
    height: .7rem;
    background: $col-txt;
    margin-right: 1rem;
    border-radius: 20rem;
    position: relative;
    top: 4.2rem;
    cursor: pointer;
    &:last-child {
      margin-right: 0;
    }
    &.active {
      background: $col-primary;
    }
  }
</style>
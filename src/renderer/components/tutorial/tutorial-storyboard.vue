<template lang="pug">
  .tutorial-box(v-if="statusShowTutorial || isFirstTimetApp")
    .tutorial-box_modal-popup
      button.close-tutorial.icon.icon-appClose(type="button" @click="closeTutorial")
      .modal-popup_step-info
        .step-info_eyes
          .eyes.eye-one
            .eye_pupil(:class="currentStepTutorial.lookEyesClass")
          .eyes.eye-two
            .eye_pupil(:class="currentStepTutorial.lookEyesClass")
        .step-info_title {{currentStepTutorial.title}}
        p.step-info_text(v-html="currentStepTutorial.text")
        .step-info_after-text
          img( alt="step image"
            v-if="currentStepTutorial.img"
            :src="currentStepTutorial.img"
          )
          button.btn--crash-course(type="button"
            v-if="currentStepTutorial.button"
            @click="currentStepTutorial.button.action"
          ) {{currentStepTutorial.button.text}}
        
      button.modal-popup_control.prev-button.icon.icon-player-play(type="button"
        @click="set_stepActive('prev')" 
        v-show="activeStep > 0"
      )
      button.modal-popup_control.next-button.icon.icon-player-play(type="button"
        @click="set_stepActive('next')" 
        v-show="activeStep < firstTutorial.length - 1"
      )
      footer.modal-popup_footer
        button.footer_skip-button(@click="skipTutorial") Skip intro

        ul.footer_all-slides-controls
          button.btn.btn--link.all-slides-controls_control( type="button"
            v-for="(control, index) in firstTutorial"
            :key="index"
            :class="{'active': activeStep === index}"
            @click="dot_stepActive(index)"
          )
</template>
<script>
export default {
  name: 'TutorialStoryboard',
  data() {
    return {
      activeStep: 0,
      firstTutorial: [
        {
          title: 'What is AI?',
          text: 'AI refers to a machine or a software program that simulates human intelligence to accomplish a certain task (often in a narrow area).',
          img: './static/img/tutorial/tutorial-1_step-1-icon.svg',
          lookEyesClass: 'look-bottom'
        },
        {
          title: 'How does it work?',
          text: 'AI learns to respond to information in a certain way, depending on what you train it for. It uses historical data and algorithms to generate a model that is able to make decisions and/or predictions.',
          img: './static/img/tutorial/tutorial-1_step-2-icon.svg',
          lookEyesClass: 'look-bottom'
        },
        {
          title: 'Where do I begin?',
          text: 'The left toolbar contains all the operations you need to build your AI model. Fret not - we’ve coded the backend for you! All you have to do is drop your desired operations onto this workspace.',
          img: './static/img/tutorial/tutorial-1_step-3-icon.svg',
          lookEyesClass: 'look-left'
        },
        {
          title: 'Customise with PerceptiLabs',
          text: 'PerceptiLabs allows you to customise everything from building your model to managing your workflow. On the right, get an overview of your project, customize your profile settings, and import/ export your favourite models.',
          img: './static/img/tutorial/tutorial-1_step-4-icon.svg',
          lookEyesClass: 'look-top-right'
        },
        {
          title: 'Don’t forget to ‘Run’',
          text: 'When you are satisfied with the neural network you have built on this workspace, be sure to hit the ‘Run’ button above to generate your AI model.',
          img: './static/img/tutorial/tutorial-1_step-5-icon.svg',
          lookEyesClass: 'look-top-left'
        },
        {
          title: 'Now you know the basics of the program. Feel free to start building your first AI!',
          text: 'Remember, this is a Beta version, if you find any errors or have any suggestions, please let us know on contact@perceptilabs.com. <br>Any feedback is highly appreciated!',
          button: {
            text: `Let's Try It`,
            action: ()=> {this.closeTutorial()}
          },
          lookEyesClass: 'look-close'
        }
      ]
    }
  },
  computed: {
    currentStepTutorial() {
      return this.firstTutorial[this.activeStep]
    },
    statusShowTutorial() {
      return this.$store.state.mod_tutorials.showTutorialStoryBoard
    },
    isFirstTimetApp() {
      return this.$store.state.mod_tutorials.firstTimeApp
    }
  },
  methods: {
    closeTutorial() {
      this.activeStep = 0;
      this.$store.commit('mod_tutorials/SET_activeStepStoryboard', this.activeStep)
      this.$store.commit('mod_tutorials/SET_showTutorialStoryBoard', false)
    },
    set_stepActive(way) {
      way === 'next' ? this.activeStep++ : this.activeStep--
      this.$store.commit('mod_tutorials/SET_activeStepStoryboard', this.activeStep)
    },
    dot_stepActive(index) {
      this.activeStep = index;
      this.$store.commit('mod_tutorials/SET_activeStepStoryboard', this.activeStep)
    },
    skipTutorial() {
      this.closeTutorial()
      //this.$store.commit('mod_tutorials/SET_firstTimeApp', false)
    }
  }
}
</script>
<style lang="scss">
  @import "../../scss/base";
  $distance-control-btn: -6rem;
  $popup-bg-gradient:linear-gradient(to top, #212328, #252931);

  .tutorial-box {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    background: rgba($bg-workspace, .7);
  }
  .tutorial-box_modal-popup {
    border: 1px solid $col-primary;
    border-radius: 1rem;
    padding: 6rem 3rem 2rem 3rem;
    position: relative;
    background: $popup-bg-gradient;
    width: 41rem;
    min-height: 35rem;
    margin-right: $w-sidebar;
    margin-left: $w-layersbar;
    display: flex;
    flex-direction: column;

    button.close-tutorial {
      color: $col-primary;
      border: 1px solid;
      position: absolute;
      top: .4rem;
      left: .4rem;
      background: none;
      border-radius: 50%;
      font-size: 1.6rem;
      padding: 0.1rem;
      z-index: 1;
    }
  }
  .step-info_eyes {
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
      margin-right: 0;
    }
  }
  .eye_pupil {
    border: 1px solid $col-primary;
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    background: $bg-workspace;
    position: absolute;
    top: 0;
    left: 0;
    transition: transform 1s;
    
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
  .step-info_title {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 2rem;
  }
  .modal-popup_step-info {
    font-size: 1.4rem;
  }
  .step-info_text {
    margin-bottom: 2rem;
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

    &.prev-button {
      left: -6rem;
      transform: translate(0, -50%) rotate(-180deg);
    }
    &.next-button {
      right: -6rem;
    }
  }
  .step-info_after-text {
    text-align: center;
  }
  .modal-popup_footer {
    margin-top: auto;
    text-align: right;
  }
  .footer_skip-button {
    color: $col-primary;
    border-bottom: 1px solid;
    font-size: 1.1rem;
    padding: 0 0 .3rem 0;
    margin-left: auto;
    background: none;
  }
  .footer_all-slides-controls {
    position: absolute;
    left: 50%;
    top: 95%;
    transform: translate(-50%, 0);
  }
  .all-slides-controls_control {
    width:  .7rem;
    height: .7rem;
    background: $col-txt;
    margin-right: 1rem;
    border-radius: 50%;
    position: relative;
    top: 4.2rem;
    &:last-child {
      margin-right: 0;
    }
    &.active {
      background: $col-primary;
    }
  }
</style>
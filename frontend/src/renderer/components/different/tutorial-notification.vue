<template lang="pug">
  .tutorial-notification(
    :data-step-code="stepCode"
    :style="styleObject"
    :class="classObject"
  )
    .tutorial-notification-content(v-html="displayText")
    .tutorial-notification-actions
      .tutorial-notification-hidetips
        span(@click.stop="onHideTipClick") Hide tips
      .tutorial-notification-got-it
        span(@click.stop="onGotItClick") Got it
</template>

<script>
export default {
  name: 'TutorialNotification',
  props: {
    stepCode: {
      type: String,
      required: true
    },
    arrowDirection: {
      type: String,
      required: true,
      validator: (value) => ['top', 'top-right', 'right', 'bottom', 'left'].includes(value)
    }
  },
  data() {
    return {
      standardSpacing: 10
    }
  },
  computed: {
    displayText() {
      return this.$store.getters['mod_tutorials/getTutorialNotificationDisplayText'](this.stepCode);
    },
    styleObject() {

      switch(this.arrowDirection) {
        case 'left':
          return {
            top: this.targetPosition.top + (this.targetPosition.height / 2 ) + 'px',
            left: this.targetPosition.left + this.targetPosition.width + this.standardSpacing + 'px'
          };
        case 'top-right':
          return {
            top: this.targetPosition.top + 'px',
            left: this.targetPosition.left - this.standardSpacing + 'px'
          };
        case 'right':
          return {
            top: this.targetPosition.top + (this.targetPosition.height / 2 ) + 'px',
            left: this.targetPosition.left - this.standardSpacing + 'px'
          };
        default:
          break;
      }
    },
    classObject() {
      return {
        'tutorial-notification--top': this.arrowDirection === 'top',
        'tutorial-notification--top-right': this.arrowDirection === 'top-right',
        'tutorial-notification--right': this.arrowDirection === 'right',
        'tutorial-notification--bottom':this.arrowDirection === 'bottom',
        'tutorial-notification--left': this.arrowDirection === 'left',
      }
    },
    targetPosition() {
      const tutorialTarget = document.querySelector(`*[data-tutorial-target="${this.stepCode}"]`);

      if (!tutorialTarget) { 
        // console.log('* !tutorialTarget', this.stepCode);
        return {
          top: 0,
          right: 0,
          bottom: 0,
          left: 0,
          width: 0,
          height: 0,
        }; 
      }

      const rect = tutorialTarget.getBoundingClientRect();
      return {
          top: rect.top,
          right: rect.right,
          bottom: rect.bottom,
          left: rect.left,
          width: rect.right - rect.left,
          height: rect.bottom - rect.top,
        }; 
    }
  },
  methods: {
    onGotItClick() {
      this.$store.dispatch('mod_tutorials/setNextStep', {currentStep: this.stepCode});
    },
    onHideTipClick() {
      // console.log('onHideTipClick!')
      this.$store.dispatch('mod_tracker/EVENT_hideTips');
      this.$store.dispatch('mod_tutorials/setTutorialNotificationsState', false);
    }
  }
}
</script>


<style lang="scss" scoped>
$tutorial-tooltip-bg: #23252A;
$tutorial-tooltip-background-picture: '/static/img/tutorial/tutorial-background.png';
$tutorial-tooltip-text-color: theme-var($neutral-8);
$arrow-size: 1rem;


.tutorial-notification {
  color: $tutorial-tooltip-text-color;
  position: absolute;
  z-index: 110;
  min-width: 15rem;
  max-width: 30rem;
  padding: 1rem 1rem;
  border-radius: 0.2rem;

  background: url($tutorial-tooltip-background-picture);
  background-size: cover; 
  box-shadow: $icon-shad;
  font-family: $base-font-sans-serif;
  text-align: left;

  border: 1px solid #5E6F9F;
  border-top: 4px solid #6185EE;
  border-radius: 2px 2px 0px 0px;
  box-sizing: border-box;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3);

  font-family: Nunito Sans;
  font-style: normal;
  font-weight: normal;
  font-size: 14px;
  line-height: 19px;

  display: flex;
  flex-direction: column;

  cursor: default;

  transform-origin: center;

  &:before {
    content: '';
    position: absolute;
    width: $arrow-size;
    height: $arrow-size;
  }
}
.tutorial-notification--top {
	&:before {
		top: 100%;
		left: 50%;
		transform: translate(-50%, -50%) rotate(45deg);
		background:$tutorial-tooltip-bg;
	}
}
.tutorial-notification--top-right {
  transform: translate(-100%, 0);
	&:before {
		top: 10%;
		left: 100%;
		transform: translate(-50%, 0) rotate(45deg);
    background:$tutorial-tooltip-bg;
    border-top: 1px solid #5E6F9F;
    border-right: 1px solid #5E6F9F;
	}
}
.tutorial-notification--right {
  transform: translate(-100%, -50%);
	&:before {
		top: 50%;
		left: 100%;
		transform: translate(-50%,-50%) rotate(45deg);
    background: $tutorial-tooltip-bg;
    border-top: 1px solid #5E6F9F;
    border-right: 1px solid #5E6F9F;
	}
}
.tutorial-notification--bottom {
  &:before {
    bottom: 100%;
    left: 50%;
    transform: translate(-50%, 50%) rotate(45deg);
    background:$tutorial-tooltip-bg;
  }
}
.tutorial-notification--left {
  transform: translateY(-50%);
  &:before {
    top: 50%;
    right: 100%;
    transform: translate(50%,-50%) rotate(45deg);
    background: $tutorial-tooltip-bg;
    border-left: 1px solid #5E6F9F;
    border-bottom: 1px solid #5E6F9F;
  }
}

.tutorial-notification-content {
  /deep/ strong {
    color: #B6C7FB;
  }
}

.tutorial-notification-actions {
  margin-top: 1rem;

  display: flex;
  justify-content: space-between;
  align-items: center;

  > * > span {
    cursor: pointer;
  }

  .tutorial-notification-hidetips {
    text-decoration: underline;
    font-size: 11px;
    line-height: 18px;
    color: #818181; 
  }

  .tutorial-notification-got-it {
    background: #6185EE;
    border: 1px solid #6185EE;
    box-sizing: border-box;
    box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    border-radius: 2px;

    span {
      padding: 0.5rem 1rem;

      font-family: Nunito Sans;
      font-style: normal;
      font-weight: 600;
      font-size: 12px;
      line-height: 16px;
    }
  }
}
</style>


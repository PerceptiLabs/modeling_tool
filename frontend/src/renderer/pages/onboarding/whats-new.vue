<template lang="pug">
  div.wrapper
    section
      .section-header
        .section-header-label What’s new in PerceptiLabs    

      .section-content
        img(:src="contentSrcForStep")

      .section-navigation
        .spacer

        .step-buttons
          .step-button(
            v-for='(c, cIdx) in contentForSteps'
            :key="cIdx"
            @click="stepNumber = cIdx"
          )
            .step-button-dot(:class="{ 'active': cIdx === stepNumber }")
        
        .navigation-action(
          v-if="stepNumber < contentForSteps.length - 1"
          @click="stepNumber++")
          svg.next-step(width="9" height="14" viewBox="0 0 9 14" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M1.01982 14L1.21612e-08 12.9802L5.98018 7L1.54787e-07 1.01982L1.01982 1.21612e-08L8.01982 7L1.01982 14Z" fill="#6185EE")

        .navigation-action(v-else)
          .get-started(@click="onGetStarted") Get started
</template>

<script>
import { mapActions } from "vuex";
import { MODAL_PAGE_PROJECT, MODAL_PAGE_WHATS_NEW } from "@/core/constants";

export default {
  name: 'PageWhatsNew',
  components: {},
  data() {
    return {
      stepNumber: 0,
      contentForSteps: [
        '../../../../static/img/whats-new/whats-new-1.png',
        '../../../../static/img/whats-new/whats-new-1.png'
      ]
    }
  },
  computed: {
    contentSrcForStep() {
      if (this.stepNumber > (this.contentForSteps.length - 1)) {
        return this.contentForSteps[0];
      }

      return this.contentForSteps[this.stepNumber];
    }
  },
  methods: {    
    ...mapActions({
      setActivePageAction:    'modal_pages/setActivePageAction',
      getDefaultModeProject:  'mod_project/getDefaultModeProject',
      closePageAction:        'modal_pages/closePageAction',
      popupNewModel:          'globalView/SET_newModelPopup',
      setCurrentView:         'mod_tutorials/setCurrentView',
      setHasShownWhatsNew:    'mod_tutorials/setHasShownWhatsNew',
    }),
    onGetStarted() {
      this.getDefaultModeProject()
        .then(_ => {
          this.popupNewModel(false);
          this.closePageAction();

          // Making sure people don't see this more than once
          this.setHasShownWhatsNew(true);

          this.setCurrentView('tutorial-model-hub-view');

          this.$router.push({ name:'projects' }).catch(err => {});
        });
    }
  },
  created() {
    this.setActivePageAction(MODAL_PAGE_WHATS_NEW);
    this.setCurrentView('tutorial-whats-new-view');
  }
}
</script>

<style lang="scss" scoped>
.wrapper {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
  border-radius: 2px;
  width: 85rem;
  height: 50rem;
  padding: 7rem 20rem;

  display: flex;
  flex-direction: column;
  align-content: center;

  > section > [class*="section-"] {
    display: flex;
    justify-content: center;
    align-items: center;
  }
}

.section-header {
  margin-bottom: 4rem;
  
  .section-header-label {
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 600;
    font-size: 24px;
    line-height: 33px;
  }
}

.section-content {
  height: 25rem;
  margin-bottom: 3rem;
}

.section-navigation {

  height: 3rem;

  .spacer {
    justify-content: flex-start;
    margin-right: auto;
    flex: 1;
  }

  .step-buttons {
    display: flex;
    justify-content: center;
    flex: 1;

    .step-button {
      
      height: 2.2rem;
      width: 2.2rem;

      display: flex;
      justify-content: center;
      align-items: center;

      cursor: pointer;

      + .step-button {
        margin-left: 0.5rem;
      }

      .step-button-dot {
        height: 1rem;
        width: 1rem;

        border-radius: 50%;

        background: #3F4C70;
       
        &.active {
          background: #6185EE;
        }
      }
    }
  }


  .navigation-action {
    display: flex;
    justify-content: center;
    margin-left: auto;
    flex: 1;

    .get-started {
      height: 3rem;
      width: 10rem;

      display: flex;
      justify-content: center;
      align-items: center;

      background: #6185EE;

      cursor: pointer;
    }

    .next-step {
      cursor: pointer;
    }
  }
}

</style>


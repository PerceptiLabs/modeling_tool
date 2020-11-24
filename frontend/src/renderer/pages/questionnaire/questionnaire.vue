
<template lang="pug">
  div.wrapper
    section
      .section-navigation
        .step-buttons
          .step-button(
            v-for='(n, nIdx) in numPages'
            :key="nIdx"
            @click="onNavigationButtonClick(nIdx)"
            :class="{ 'disabled': !isNavigationAllowed(nIdx) }"
          )
            .step-button-dot(:class="{ 'active': nIdx === pageNumber }")
      
      .section-content
        training-frequency(
          v-if="pageNumber === 0"
          v-model="questionnairePages['TrainingFrequency']")

        reason-for-use(
          v-else-if="pageNumber === 1"
          v-model="questionnairePages['ReasonForUse']")
        
        //- the last page shown depending on the answer on page 1
        //- 'part-of-ml-team', 'develop-ml-tools', 'curious-about-ml' can be
        //- found in the reason-for-use.vue file
        team-size(
          v-else-if="pageNumber > 1 && reasonForUseAnswer === 'part-of-ml-team'"
          v-model="questionnairePages['TeamSize']")
        framework-preference(
          v-else-if="pageNumber > 1 && reasonForUseAnswer === 'develop-ml-tools'"
          v-model="questionnairePages['FrameworkPreference']")
        learning-resource(v-else-if="pageNumber > 1 && reasonForUseAnswer === 'curious-about-ml'"
          v-model="questionnairePages['LearningResource']")

      .section-action
        .button-group
          button(type="button"
            @click="onCancel"
            ) Cancel
          button.cta(v-if="pageNumber < lastPageIndex"
            type="button"
            @click="onNext"
            ) Next
          button.cta(v-else
            type="button"
            @click="onConfirm"
            ) Confirm
</template>

<script>
import { MODAL_PAGE_WHATS_NEW } from "@/core/constants";

import TrainingFrequency from "@/components/questionnaire/training-frequency.vue";
import ReasonForUse from "@/components/questionnaire/reason-for-use.vue";
import TeamSize from "@/components/questionnaire/team-size.vue";
import FrameworkPreference from "@/components/questionnaire/framework-preference.vue";
import LearningResource from "@/components/questionnaire/learning-resource.vue";

export default {
  name: 'PageQuestionnaire',
  components: { TrainingFrequency, ReasonForUse, TeamSize, FrameworkPreference, LearningResource },
  data() {
    return {
      pageNumber: 0,
      numPages: 3,
      questionnairePages: {
        'TrainingFrequency': {},
        'ReasonForUse': {},
        'TeamSize': {},
        'FrameworkPreference': {},
        'LearningResource': {}
      },
    }
  },
  mounted() {
    document.addEventListener('keydown', this.keysNavigationHandler);
  },
  destroyed() {
    document.removeEventListener('keydown', this.keysNavigationHandler);
  },
  methods: {
    isNavigationAllowed(targetPageNumber) {
      // the logic for allowing the move to the next screen
      if (targetPageNumber < 0) { return false; }
      if (targetPageNumber > this.lastPageIndex) { return false; }

      // 0-indexed page numbers
      if (targetPageNumber === 1 && !this.hasAnswerPage1) { return false; }
      if (targetPageNumber === 2 && !this.hasAnswerPage2) { return false; }

      return true;
    },
    onNavigationButtonClick(nIdx) {
      if (!this.isNavigationAllowed(nIdx)) { return; }

      this.pageNumber = nIdx;
    },
    keysNavigationHandler(event) {
      event.stopPropagation();

      const key = event.key;
      if(key === 'ArrowLeft' && this.pageNumber > 0) {
        this.pageNumber--;
      } else if(key === 'ArrowRight' && this.isNavigationAllowed(this.pageNumber + 1)) {
        this.pageNumber++;
      } else if(key === 'Enter' && this.pageNumber === this.lastPageIndex) {
        this.onConfirm();
      }
    },
    async onCancel() {
      await this.$store.dispatch('mod_questionnaire/sendFirstLoginStatus');
      this.exitQuestionnaire();
    },
    onNext() {
      if (!this.isNavigationAllowed(this.pageNumber + 1)) { return; }
      
      this.pageNumber++;
    },
    async onConfirm() {
      const qaPayload = Object.values(this.questionnairePages).filter(p => JSON.stringify(p) !== '{}');

      // sending to MixPanel
      this.$store.dispatch('mod_tracker/EVENT_questionnaireSubmitted', { answers: qaPayload });
      
      // sending to KeyCloak
      await this.$store.dispatch('mod_questionnaire/sendQuestionnaireResponses', qaPayload);
      this.exitQuestionnaire();
    },
    exitQuestionnaire() {      
      if (!this.$store.getters['mod_tutorials/getHasShownWhatsNew']) {
        this.$store.dispatch('modal_pages/setActivePageAction', MODAL_PAGE_WHATS_NEW);
      } else {
        this.$store.dispatch('modal_pages/closePageAction');
      }
    }
  },
  computed: {
    lastPageIndex() {
      return this.numPages - 1;
    },
    hasAnswerPage1() {
      const result = this.questionnairePages['TrainingFrequency'];
      if (!result || !result.a) { return false; }

      return !!result.a.trainingFrequency;
    },
    hasAnswerPage2() {
      const result = this.questionnairePages['ReasonForUse'];
      if (!result || !result.a) { return false; }

      return !!result.a.reasonForUse;
    },
    reasonForUseAnswer() {
      // what's shown on the 3rd page is decided by the choice on the 2nd.
      const result = this.questionnairePages['ReasonForUse'];
      if (!result || !result.a) { return false; }

      return result.a.reasonForUse;
    }
  }
}
</script>

<style lang="scss" scoped>
$questionnarie-background-picture: '/static/img/questionnarie/background1.png';

.wrapper {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: linear-gradient(-72.32deg, #383F50 -15.94%, #23252A 137.98%);
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
  border-radius: 2px;
  width: 38rem;
  height: 45rem;  

  > section {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    
    background: url($questionnarie-background-picture);
    background-position: right;
    background-size: contain;
    background-repeat: no-repeat;

    width: 100%;
    height: 100%;
  }
}

.section-navigation {
  margin-top: 2rem;
  height: 3rem;

  .step-buttons {
    display: flex;
    justify-content: center;
    align-items: center;
    
    height: 100%;

    .step-button {     
      display: flex;
      justify-content: center;
      align-items: center;

      height: 2.2rem;
      width: 2.2rem;

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

      &.disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }
    }
  }

}

.section-content {
  width: 100%;
  margin-top: 2rem;

  /deep/ h3 {
    text-align: left;
    margin: 0 4rem 2rem 4rem;

    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 600;
    font-size: 20px;
    line-height: 19px;
  }

  /deep/ p {
    margin-top: 1rem;
    text-align: center;

    font-family: Nunito Sans;
    font-style: normal;
    font-weight: normal;
    font-size: 16px;
    line-height: 16px;
  }

  /deep/ .content-group {
    display: flex;
    flex-direction: column;

    margin: 0 4rem;
  }

  /deep/ base-radio span {
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: normal;
    font-size: 16px;
    line-height: 22px;
  }

  /deep/ textarea {
    background: transparent;
    height: 8rem;

    color: #fff;
    font-size: 14px;

    border: 1px solid #5E6F9F;
    box-sizing: border-box;
    border-radius: 2px;

    margin-top: 2rem;

    resize: none;
  }

  /deep/ .checkbox-group {
    
    /deep/ .checkbox-fake {
      background: transparent;
      border: 1px solid #5E6F9F;
    }

    & + .checkbox-group {
      margin-top: 1.5rem;
    }
  }
}

.section-action {
  width: 100%;

  margin-top: auto;
  margin-bottom: 3rem;
  padding: 0 4rem;

  display: flex;
  justify-content: flex-end;

  .button-group {
    
    button {
      width: 10.5rem;
      height: 3.5rem;

      box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
      border-radius: 2px;

      background: #363E51;
      color: #E1E1E1;

      font-family: Nunito Sans;
      font-style: normal;
      font-weight: normal;
      font-size: 14px;
      line-height: 19px;

      + button {
        margin-left: 1rem;
      }

      &.cta {
        background: #6185EE;
        border: 1px solid #6185EE;
      }
    }
  }
}
  

</style>


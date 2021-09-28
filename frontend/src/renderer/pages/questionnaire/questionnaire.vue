
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
        type-of-model-you-build(
          v-if="pageNumber === 0"
          v-model="questionnairePages['TypeOfModelYouBuild']")
        deep-learning-experience(
          v-else-if="pageNumber === 1"
          v-model="questionnairePages['DeepLearningExperience']")
        intergalactic-journey(
          v-else-if="pageNumber === 2"
          v-model="questionnairePages['IntergalacticJourney']")
        what-role-do-you-have(
          v-else-if="pageNumber === 3"
          v-model="questionnairePages['WhatRoleDoYouHave']")
        what-are-you-looking-for(
          v-else-if="pageNumber === 4"
          v-model="questionnairePages['WhatAreYouLookingFor']")
       
      .section-action
        .button-group
          button.btn.btn--secondary(type="button"
            @click="onCancel"
            ) Cancel
          button.btn.btn--primary(v-if="pageNumber < lastPageIndex"
            type="button"
            @click="onNext"
            ) Next
          button.btn.btn--primary(v-else
            type="button"
            @click="onConfirm"
            ) Confirm
</template>

<script>
import TypeOfModelYouBuild from "@/components/questionnaire/type-of-model-you-build.vue";
import DeepLearningExperience from "@/components/questionnaire/deep-learning-experience.vue";
import IntergalacticJourney from "@/components/questionnaire/Intergalactic-journey.vue";
import WhatRoleDoYouHave from "@/components/questionnaire/what-role-do-you-have.vue";
import WhatAreYouLookingFor from "@/components/questionnaire/what-are-you-looking-for.vue";

export default {
  name: 'PageQuestionnaire',
  components: { 
    TypeOfModelYouBuild,
    DeepLearningExperience,
    IntergalacticJourney,
    WhatRoleDoYouHave,
    WhatAreYouLookingFor,
  },
  data() {
    return {
      pageNumber: 0,
      numPages: 5,
      questionnairePages: {
        'TypeOfModelYouBuild': {},
        'DeepLearningExperience': {},
        'IntergalacticJourney': {},
        'WhatRoleDoYouHave': {},
        'WhatAreYouLookingFor': {},
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
      if (targetPageNumber === 1 && !this.hasAnswerFor('TypeOfModelYouBuild')) { return false; }
      if (targetPageNumber === 2 && !this.hasAnswerFor('DeepLearningExperience')) { return false; }
      if (targetPageNumber === 3 && !this.hasAnswerFor('IntergalacticJourney')) { return false; }
      if (targetPageNumber === 4 && !this.hasAnswerFor('WhatRoleDoYouHave')) { return false; }

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
      } else if(key === 'Escape') {
        this.onCancel();
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
      this.$store.dispatch('modal_pages/closePageAction');
      // Was commented in case we want to enable back wat's new tips.
      // if (!this.$store.getters['mod_tutorials/getHasShownWhatsNew']) {
      //   this.$store.dispatch('modal_pages/setActivePageAction', MODAL_PAGE_WHATS_NEW);
      // } else {
      //   this.$store.dispatch('modal_pages/closePageAction');
      // }
    },
    hasAnswerFor(valueKey) {
      const result = this.questionnairePages[valueKey];
      if (!result || !result.a) { return false; }
      return !!result.a[valueKey];
    },
  },
  computed: {
    lastPageIndex() {
      return this.numPages - 1;
    },
  }
}
</script>

<style lang="scss" scoped>
$questionnaire-background-picture: '/static/img/questionnarie/background1.png';

.wrapper {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  // background: linear-gradient(-72.32deg, #383F50 -15.94%, #23252A 137.98%);
  background: theme-var($neutral-8);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
  border-radius: 2px;
  width: 38rem;
  height: 46rem;  

  > section {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;

    background: url($questionnaire-background-picture) no-repeat right;
    background-size: contain;
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
    display: flex;
    button {
      // width: 10.5rem;
      // height: 3.5rem;

      // box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
      // border-radius: 2px;

      // background: #363E51;
      // color: #E1E1E1;

      // font-family: Nunito Sans;
      // font-style: normal;
      // font-weight: normal;
      // font-size: 14px;
      // line-height: 19px;

      + button {
        margin-left: 1rem;
      }

      // &.cta {
      //   background: #6185EE;
      //   border: 1px solid #6185EE;
      // }
    }
  }
}
  

</style>


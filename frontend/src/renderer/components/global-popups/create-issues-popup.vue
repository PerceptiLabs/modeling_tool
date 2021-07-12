<template lang="pug">
  base-global-popup(:tab-set="popupTitle" @closePopup="cancel")
    //- This is the form
    //- The confirmation is below
    template(v-if="isForm")
      template(slot="Report to PerceptiLabs-content")
        .popup-body-section(
          data-testing-target="report-modal"
        )
          view-loading(:isLoading="isRequesting")
          .section-header
            i.icon.icon-bug-report.section-header-icon 
            .section-header-label Report a bug

          .section-content
            span Title
            input.section-content-input(
              v-model="issueTitle"
              ref="issueTitle")

          .section-content
            span Comments
            textarea.section-content-textarea(
              v-model="issueBody"
              ref="issueBody")

          //- .section-content.post-as-section
          //-   .section-content-label Post as:
          //-   .section-content-radio-group
          //-     base-radio(group-name="postas-group" value-input="normal" v-model="issueType" :disabled="true")
          //-       span Username
          //-     base-radio(group-name="postas-group" value-input="anonymous" v-model="issueType")
          //-       span Anonymous

      template(slot="action")
        button.btn.btn--primary.btn--disabled(type="button"
          @click="cancel"
          ) Cancel
        button.btn.btn--primary(type="button"
          @click="ok"
          ) Post

      template(slot="after-footer")
        .after-footer-section
          .section-header
            svg.section-header-icon(width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg")
              path(fill-rule="evenodd" clip-rule="evenodd" d="M0 1.25C0 0.918479 0.131696 0.600537 0.366117 0.366117C0.600537 0.131696 0.918479 0 1.25 0L8.75 0C9.08152 0 9.39946 0.131696 9.63388 0.366117C9.8683 0.600537 10 0.918479 10 1.25V6.25C10 6.58152 9.8683 6.89946 9.63388 7.13388C9.39946 7.3683 9.08152 7.5 8.75 7.5H2.75875C2.593 7.50004 2.43406 7.56591 2.31687 7.68313L0.53375 9.46625C0.490082 9.51003 0.434407 9.53987 0.373773 9.55199C0.313138 9.56412 0.25027 9.55798 0.193125 9.53436C0.135979 9.51074 0.0871262 9.4707 0.0527483 9.4193C0.0183704 9.3679 1.31343e-05 9.30746 0 9.24563L0 1.25ZM2.1875 1.875C2.10462 1.875 2.02513 1.90792 1.96653 1.96653C1.90792 2.02513 1.875 2.10462 1.875 2.1875C1.875 2.27038 1.90792 2.34987 1.96653 2.40847C2.02513 2.46708 2.10462 2.5 2.1875 2.5H7.8125C7.89538 2.5 7.97487 2.46708 8.03347 2.40847C8.09208 2.34987 8.125 2.27038 8.125 2.1875C8.125 2.10462 8.09208 2.02513 8.03347 1.96653C7.97487 1.90792 7.89538 1.875 7.8125 1.875H2.1875ZM2.1875 3.4375C2.10462 3.4375 2.02513 3.47042 1.96653 3.52903C1.90792 3.58763 1.875 3.66712 1.875 3.75C1.875 3.83288 1.90792 3.91237 1.96653 3.97097C2.02513 4.02958 2.10462 4.0625 2.1875 4.0625H7.8125C7.89538 4.0625 7.97487 4.02958 8.03347 3.97097C8.09208 3.91237 8.125 3.83288 8.125 3.75C8.125 3.66712 8.09208 3.58763 8.03347 3.52903C7.97487 3.47042 7.89538 3.4375 7.8125 3.4375H2.1875ZM2.1875 5C2.10462 5 2.02513 5.03292 1.96653 5.09153C1.90792 5.15013 1.875 5.22962 1.875 5.3125C1.875 5.39538 1.90792 5.47487 1.96653 5.53347C2.02513 5.59208 2.10462 5.625 2.1875 5.625H5.3125C5.39538 5.625 5.47487 5.59208 5.53347 5.53347C5.59208 5.47487 5.625 5.39538 5.625 5.3125C5.625 5.22962 5.59208 5.15013 5.53347 5.09153C5.47487 5.03292 5.39538 5 5.3125 5H2.1875Z" fill="#B6C7FB")
            .section-header-label Ask our forum

          .section-content.left-indent
            .section-content-text Get answers from PerceptiLabs' community forum
            a.section-content-link(:href="forumLink" target="_blank") here
            | .

    
    //- This is the confirmation portion
    template(v-else)
      template(slot="Report to PerceptiLabs-content")
        .popup-body-section.ma-2
          .section-content.center
            span Posted successfully
          .section-content.center
            span Your post is now live on PerceptiLabs' GitHub issues page.

      template(slot="action")
        .action-section
          button.btn.btn--primary(type="button"
            @click="viewIssue"
            ) View Issue
</template>

<script>
  import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";
  import { createIssueInGithub } from '@/core/apiRygg';
  import ViewLoading from '@/components/different/view-loading.vue'
  import { PERCEPTILABS_FORUM_URL } from "@/core/constants";

  export default {
    name: "CreateIssuesPopup",
    components: { BaseGlobalPopup, ViewLoading },
    props: {
      confirmCallback: {
        type: Function,
        default: () => {}
      },
      cancelCallback: {
        type: Function,
        default: () => {}
      },
    },
    data() {
      return {
        isForm: true,
        issueTitle: '',
        issueBody: '',
        issueType: 'anonymous',
        popupTitle: ['Report to PerceptiLabs'],
        forumLink: PERCEPTILABS_FORUM_URL,
        gitHubIssuesUrl: 'https://github.com/PerceptiLabs/PerceptiLabs/issues/',
        gitHubIssueNumber: '',
        isRequesting: false,
      }
    },
    methods: {
      ok() {

        const requestPayload = {
          'title': this.issueTitle,
          'body': this.issueBody,
          'issue_type': this.issueType,
          'github_token': ''
        };

        if (this.issueTitle && this.issueBody) {
          this.isRequesting = true
          createIssueInGithub(requestPayload)
            .then(res => {
              if (!res.data) { return; }
              this.isForm = false;

              this.gitHubIssueNumber = res.data['Issue Number'];
            
              const kernelLogPayload = {
                'issueTitle': this.issueTitle,
                'issueBody': this.issueBody,
                'gitHubIssueNumber': this.gitHubIssueNumber,
                'gitHubIssueUrl': `${this.gitHubIssuesUrl}${this.gitHubIssueNumber}`,
              };

              this.$store.dispatch('mod_api/API_UploadKernelLogs', kernelLogPayload);

              this.issueTitle = '';
              this.issueBody = '';

            }).finally(() => this.isRequesting = false);
        } else {
          if (this.$refs['issueTitle']) {
            this.$refs['issueTitle'].classList.add('has-error');
          }
          if (this.$refs['issueBody']) {
            this.$refs['issueBody'].classList.add('has-error');
          }
        }
      },
      cancel() {
        this.cancelCallback();
        this.closePopup();
      },
      viewIssue() {
        window.open(`${this.gitHubIssuesUrl}${this.gitHubIssueNumber}`, '_blank');
        this.closePopup();
      },
      closePopup() {
        this.$store.commit('globalView/set_createIssuesPopup', false);
      }
    }
  }
</script>

<style scoped lang="scss">
  @import "../../scss/base";
  @import "../../scss/common/info-popup";

  /deep/ .popup_header {
    cursor: default;
  }

  /deep/ .settings-layer_section {
    padding: 0;
  }

  /deep/ .popup_foot {
    padding-right: 1.5rem;
  }

  .popup-body-section {
    padding: 1.5rem;

    &.ma-2 {
      margin: 2rem;
    }

    .section-header + .section-content {
      margin-top: 1.5rem;
    }
  }

  .after-footer-section {
    border-top: 1px solid #3F4C70;
    padding: 1.5rem;
  }

  .post-as-section {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .section-content-radio-group {

      /deep/ .custom-radio:last-of-type {
        padding-right: 0;
      }
    }
  }

  .section-header {
    display: flex;
    align-items: center;
    
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: bold;
    font-size: 12px;
    line-height: 16px;
    display: flex;
    align-items: center;
    
    color: #B6C7FB;

    .section-header-icon {
      height: 1.2rem;
      width: 1.2rem;
      font-size: 1.2rem;
    }

    .section-header-icon + .section-header-label {
      margin-left: 0.8rem;
    }
  }

  .section-content {
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 300;
    font-size: 12px;
    line-height: 16px;

    color: #FFFFFF;

    &.left-indent {
      margin-left: 2rem;
    }

    &.center {
      display: flex;
      justify-content: center;
    }

    .section-content-text {
      display: flex;
      align-items: center;
    }

    .section-content-link {
      font-weight: bold;
      color: #7397FE;
    }

    .section-content-input {
      background: transparent;

      border: 1px solid #5E6F9F;
      box-sizing: border-box;
      border-radius: 2px;

      margin-top:0.5rem;

      &.has-error {
        border: 1px solid #fe7373;
      }
    }

    .section-content-textarea {
      background: transparent;
      height: 10rem;

      border: 1px solid #5E6F9F;
      box-sizing: border-box;
      border-radius: 2px;

      margin-top:0.5rem;

      &.has-error {
        border: 1px solid #fe7373;
      }
    }

    + .section-content {
      margin-top: 1rem;
    }
  }

  .action-section {
    width: 100%;
    display: flex;
    justify-content: center;
  }
</style>

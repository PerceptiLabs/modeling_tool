<template lang="pug">
  base-global-popup(:tab-set="popupTitle")
    template(slot="Report to PerceptiLabs-content")
      .popup-body-section
        .section-header
          i.icon.icon-bug-report.section-header-icon 
          .section-header-label There's a bug

        .section-content
          span Comments
          textarea.section-content-textarea(
            v-model="issueBody"
            ref="issueTextArea")

    template(slot="action")
      button.btn.btn--primary.btn--disabled(type="button"
        @click="cancel"
        ) Cancel
      button.btn.btn--primary(type="button"
        @click="ok"
        ) Send

    template(slot="after-footer")
      .after-footer-section
        .section-header
          img.section-header-icon(src="./../../../../static/img/slack.png")
          .section-header-label Connect on Slack

        .section-content.left-indent
          .section-content-text Ask and get answers from PerceptiLabs' community Slack channel. 
          a.section-content-link(:href="slackLink" target="_blank") Take me there.
        

</template>

<script>
  import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";

  import axios from 'axios';

  export default {
    name: "CreateIssuesPopup",
    components: {BaseGlobalPopup},
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
        issueBody: '',
        popupTitle: ['Report to PerceptiLabs'],
        slackLink: 'https://join.slack.com/t/perceptilabs-com/shared_invite/enQtODQ5NzAwNDkxOTExLWUxODAwZDk0MzA1MmM4OTViNWE4MmVjYjc2OTQwMTQ4N2NmM2ZlYmI5NjZjOWRiYjBkYjBjMTMzNjEyMDNiNDk'
      }
    },
    methods: {
      ok() {

        const payload = {
          'title': `User Issue ${(new Date).toISOString()}`,
          'body': this.issueBody
        };

        if (this.issueBody) {
          this.$store.dispatch('mod_issues/createIssue', payload)
            .then(res => {
              this.issueBody = '';
              this.closePopup();
            });
        } else if (this.$refs['issueTextArea']) {
          this.$refs['issueTextArea'].classList.add('has-error');
        }
      },
      cancel() {
        this.cancelCallback();
        this.closePopup();
      },
      closePopup() {
        this.$store.commit('globalView/HIDE_allGlobalPopups');
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
  }

  .after-footer-section {
    border-top: 1px solid #3F4C70;
    padding: 1.5rem;

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

    .section-content-text {
      display: flex;
      align-items: center;
    }

    .section-content-link {
      font-weight: bold;
      color: #7397FE;
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
  }
</style>

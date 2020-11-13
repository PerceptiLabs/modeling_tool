<template lang="pug">
  .sidebar-auto-setting-info(
    v-if="shouldDisplay"
  )
    p.message Settings for this component will no longer update automatically. Reset component to enable auto-settings.
    .d-flex.align-items-center
      base-checkbox.w-100(v-model="dontShowThisAgain" :isNewUi="true")
        span.dont-show-text Do not show this again
      span.dismiss-btn(@click="onDismiss") Dismiss
</template>
<script>

const shouldShowSidebarAutosettingInfo = 'shouldShowSidebarAutosettingInfoConst';

export default {
  name: "SidebarAutoSettingInfo",
  data() {
    return {
      shouldDisplay: false,
      shouldShowSidebarAutosettingInfo: JSON.parse(localStorage.getItem(shouldShowSidebarAutosettingInfo)) === null,
      dontShowThisAgain: false,
    }
  },
  props: {
    selectedEl: {
      type: Object,
      default: function(){return {}}
    }
  },
  computed: {
    isDataComponent() {
      const componentName = this.selectedEl.componentName;
      
      return ['DataData', 'DataEnvironment', 'DataRandom'].includes(componentName);
    }
  },
  watch: {
    'selectedEl.visited': {
      handler(currentVisited, previousVisited){
        if(currentVisited === true
          && previousVisited === false
          && this.shouldShowSidebarAutosettingInfo
          && !this.isDataComponent) {
          this.shouldDisplay = true;
        }
      }
    }
  },
  methods: {
    onDismiss() {
      if(this.dontShowThisAgain) {
        this.shouldShowSidebarAutosettingInfo = false;
        localStorage.setItem(shouldShowSidebarAutosettingInfo, false);
      }
      this.shouldDisplay = false;
    }
  }
}
</script>
<style lang="scss">
.sidebar-auto-setting-info {
  position: absolute;
  width: 230px;
  left: -252px;
  top: 0;
  padding: 10px 15px;
  background: #131B30;
  border: 1px solid rgba(97, 133, 238, 0.4);
  box-sizing: border-box;
  border-radius: 1px;
  &:after {
    content: '';
    position: absolute;
    top: 10px;
    right: -5px;
    display: block;
    width: 10px;
    height: 10px;
    background: #131B30;
    border-top: 1px solid rgba(97, 133, 238, 0.4);
    border-right: 1px solid rgba(97, 133, 238, 0.4);
    transform: rotate(45deg);
  }
}
.message {
  font-family: Nunito Sans;
  font-size: 12px;
  line-height: 14px;
  color: #B6C7FB;
}
.dismiss-btn {
  font-family: Nunito Sans;
  font-weight: 600;
  font-size: 11px;
  line-height: 14px;
  color: #6185EE;
  &:hover {
    cursor: pointer;
    text-decoration: underline;
  }
}
.dont-show-text {
  display: block;
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 300;
  font-size: 11px;
  line-height: 14px;
  color: #5E6F9F;
}
.w-100 {
  width: 100%;
}
</style>
<template lang="pug">
  .settings-layer_section(
    :class="{'code_full-view': fullView}"
  )
    .bookmark_head
      ul.bookmark_tab-list(v-if="isMultiTabs")
        button.bookmark_tab(type="button"
          v-for="(data, key) in theCode"
          :key="data.key"
          :class="{'bookmark_tab--active': currentTab === key}"
          @click="currentTab = key"
          ) {{ key }}
      .bookmark_tab.bookmark_tab--active(v-else) Output
      button.btn.btn--link.icon.icon-full-screen-code(type="button" @click="toggleFullView")
    .bookmark_content
      code-hq.code-wrap(
        v-if="isMultiTabs && theCode"
        v-model="theCode[currentTab]"
        )
      code-hq.code-wrap(
        v-else
        v-model="theCode"
        )

</template>

<script>
  import codeHq    from "@/components/network-elements/elements-settings/code-hq.vue";

export default {
  name: "SettingsCode",
  components: {codeHq},
  props: {
    trainingMode: {
      type: Boolean,
      default: false
    },
    theCode: {
      type: [String, Object],
      default: ''
    },
  },
  created () {
    if(this.isMultiTabs) {
      let keys = Object.keys(this.theCode);
      this.currentTab = keys[0];
    }
  },
  data() {
    return {
      currentTab: '',
      fullView: false
    }
  },
  computed: {
    isMultiTabs() {
      return typeof this.theCode === 'string' ? false : true
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView;
      document.querySelector('.popup_body').classList.toggle("popup_body--show-code");
      document.querySelector('.network-field').classList.toggle("network-field--show-code");
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "../../../scss/base";
  .bookmark_head {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .bookmark_tab-list {
    padding: 0;
  }
  .bookmark_tab {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 7em;
    text-align: left;
    height: 2rem;
    margin-right: 1px;
  }
  .bookmark_content {
    position: relative;
  }
  .btn--code-view {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 100%;
    width: 1rem;
    background: linear-gradient(to left, rgba(#fff, 0), rgba(#fff, .35), rgba(#fff, 0));
    color: $col-primary;
    &:hover {
      background: linear-gradient(to left, rgba(#fff, 0), rgba(#fff, .2), rgba(#fff, 0));
    }
  }
  .code_full-view {
    display: flex;
    flex: 1;
    flex-direction: column;
    width: 100%;
    .code-wrap,
    .bookmark_content {
      height: 100%;
    }
  }
</style>
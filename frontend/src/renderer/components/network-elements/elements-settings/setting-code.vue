<template lang="pug">
  .settings-layer_section(
    :class="{'code_full-view': fullView}"
  )
    .bookmark_head
      ul.bookmark_tab-list
        button.bookmark_tab(type="button"
          v-for="(data, key) in theCode"
          :key="data.key"
          :class="{'bookmark_tab--active': currentTab === key}"
          @click="currentTab = key"
          ) {{ key }}
        button.bookmark_tab.bookmark_tab--error(type="button"
          v-if="errorData"
          :class="{'bookmark_tab--active': currentTab === 'error'}"
          @click="currentTab = 'error'"
        ) Error
      //.bookmark_tab.bookmark_tab--active(v-else) Output
      button.btn.btn--link.icon.icon-full-screen-code(type="button" @click="toggleFullView")
    .bookmark_content
      code-hq.code-wrap(
        v-if="theCode && currentTab !== 'error'"
        v-model="theCode[currentTab]"
        :error-row="errorRow"
        )
      .code-wrap(v-if="currentTab === 'error'")
        .code-wrap_error-container
          p.text-warning {{ errorData.Message }}

</template>

<script>
  import codeHq    from "@/components/network-elements/elements-settings/code-hq.vue";

export default {
  name: "SettingsCode",
  components: {codeHq},
  props: {
    // trainingMode: {
    //   type: Boolean,
    //   default: false
    // },
    currentEl: {
      type: Object,
    },
    value: {
      type: [String, Object],
      default: ''
    },
  },
  created () {
    const code = this.currentEl.layerCode.length ? {'Output': this.currentEl.layerCode} : this.theCode;
    const keys = Object.keys(code);
    this.currentTab = keys[0];
  },
  beforeDestroy() {
    this.closeFullView()
  },
  data() {
    return {
      currentTab: '',
      fullView: false,
    }
  },
  computed: {
    // isMultiTabs() {
    //   return typeof this.theCode === 'string' ? false : true
    // },
    theCode: {
      get: function() {
        return this.value
      },
      set: function(newValue) {
        this.$emit('input', newValue);
      }
    },
    errorData() {
      return this.currentEl.layerCodeError
    },
    errorRow() {
      return !!this.errorData ? this.errorData.Row : 0
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView;
      document.querySelector('.popup_body').classList.toggle("popup_body--show-code");
      document.querySelector('.network').classList.toggle("network--show-code");
    },
    closeFullView() {
      this.fullView = false;
      document.querySelector('.network').classList.remove("network--show-code");
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
    z-index: 1;
  }
  .bookmark_tab--error {
    background: $col-warning;
    margin-left: -1em;
    z-index: 0;
    &.bookmark_tab--active {
      z-index: 2;
    }
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
  .code-wrap {
    height: 30rem;
    font-size: 1.6rem;
  }
  .code-wrap_error-container {
    overflow: scroll;
    height: 100%;
  }
</style>
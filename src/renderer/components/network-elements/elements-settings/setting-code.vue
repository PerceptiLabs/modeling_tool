<template lang="pug">
  .settings-layer(
    :class="{'settings-layer--full-view': fullView}"
  )
    .settings-layer_section
      ul.bookmark_tab-list(v-if="isMultiTabs")
        button.bookmark_tab(type="button"
          v-for="(data, key) in theCode"
          :key="data.key"
          :class="{'bookmark_tab--active': currentTab === key}"
          @click="currentTab = key"
          ) {{ key }}
      .bookmark_content
        .form_holder(v-if="isMultiTabs && theCode")
          code-hq( v-model="theCode[currentTab]" )
        .form_holder(v-else)
          code-hq( v-model="theCode" )
        button.btn.btn--code-view.icon.icon-shevron-right(type="button" @click="toggleFullView")

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
      this.fullView = !this.fullView
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "../../../scss/base";
  .settings-layer {
    max-width: 29rem;
    overflow: hidden;
  }
  .settings-layer--full-view {
    max-width: none;
    .btn--code-view:before {
      transform: rotate(180deg);
      display: inline-block;
    }
  }
  .bookmark_tab-list {
    padding: 0;
  }
  .bookmark_tab {
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
</style>
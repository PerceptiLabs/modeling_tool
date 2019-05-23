<template lang="pug">
  .settings-layer
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
    }
  },
  computed: {
    isMultiTabs() {
      return typeof this.theCode === 'string' ? false : true
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
  .bookmark_tab-list {
    padding: 0;
  }
  .bookmark_tab {
    min-width: 7em;
    text-align: left;
    height: 2rem;
    margin-right: 1px;
  }
</style>
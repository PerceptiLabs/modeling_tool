<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabSet"
        :key="tab.i"
        :class="{'disable': tabSelected != tab}"
        @click="setTab(tab)"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body.active(
        v-for="(tabContent, i) in tabSet"
        :key="tabContent.i"
        v-if="tabSelected === tabContent"
        )
        .settings-layer
          slot(:name="tabContent+'-content'")
        .settings-layer_foot
          slot(:name="tabContent+'-action'")
            button.btn.btn--primary(type="button" @click="applySettings(tabContent)" :id="idSetBtn") Apply
            button.btn.btn--dark-blue-rev(type="button"
              v-if="showUpdateCode"
              @click="updateCode"
              ) Update code

</template>

<script>
export default {
  name: 'NetBaseSettings',
  props: {
    tabSet: {
      type: Array,
      default: function() {
        return ['Settings', 'Code']
      }
    },
    firstTab: {
      type: String,
      default: ''
    },
    layerCode: {
      type: [Number, Object, String],
      default: 0
    },
    idSetBtn: {
      type: String,
      default: ''
    },
  },
  mounted() {
    let tab = this.firstTab || this.tabSet[0];
    this.setTab(tab)
    //console.log(!!this.layerCode);
  },
  data() {
    return {
      tabSelected: '',
    }
  },
  computed: {
    showUpdateCode() {
      return this.tabSelected === 'Settings' && !!this.layerCode
    }
  },
  methods: {
    setTab(name) {
      this.tabSelected = name;
    },
    applySettings(name) {
      this.$emit('press-apply', name)
    },
    updateCode(name) {
      this.$emit('press-update')
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../../scss/base";
  .popup {
    min-width: 29rem;
    box-shadow: $layer-shad;
  }
  .popup_body {
    max-width: calc(50vw - #{$w-sidebar});
    min-width: 29rem;
    overflow: hidden;
  }
  .settings-layer {
    max-height: calc(100vh - 26rem);
    overflow: auto;
  }
  .popup_body--show-code {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    top: 0;
    max-width: none;
    background-color: $bg-toolbar;
    .settings-layer {
      max-height: none;
    }
  }
</style>

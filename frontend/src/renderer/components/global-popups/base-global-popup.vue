<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      ul.popup_tab-set
        button.popup_header(
          v-for="(tab, i) in tabSet"
          :key="tab.i"
          @click="setTab(tab)"
          :class="{'disable': tabSelected != tab}"
        )
          h3(v-html="tab")

      .popup_tab-body
        .settings-layer_section(
          v-for="(tabContent, i) in tabSet"
          :key="tabContent.i"
          v-if="tabSelected === tabContent"
        )
          slot(:name="tabContent+'-content'")

      .popup_foot
        slot(name="action")
          button.btn.btn--primary(type="button"
            @click="closePopup()") Cancel

</template>

<script>
import { mapActions } from 'vuex';
export default {
  name: "BaseGlobalPopup",
  props: {
    tabSet: {
      type: Array,
      default: function() {
        return ['']
      }
    },
  },
  mounted() {
    this.setTab(this.tabSet[0])
  },
  data() {
    return {
      tabSelected: '',
    }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    setTab(name) {
      this.tabSelected = name;
    },
    closePopup() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
    }
  }
}
</script>

<style lang="scss" scoped>
  .settings-layer_section {
    width: 100%;
  }
</style>

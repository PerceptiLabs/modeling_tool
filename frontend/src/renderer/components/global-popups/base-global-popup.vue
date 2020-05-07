<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup-background
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
    this.setTab(this.tabSet[0]);
    this.$store.dispatch('mod_events/SET_enableCustomHotKey', false);
  },
  beforeDestroy() {
    this.$store.dispatch('mod_events/SET_enableCustomHotKey', true);
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
  @import "../../scss/base";
  
  .settings-layer_section {
    width: 100%;
  }

  .popup_foot {
    .btn.btn--primary {

      width: 9.5rem;
      height: 3.5rem;
      background-color: $color-6;
      color: $white;

      &:not(.btn--disabled) {
        background: $color-6;
        border: 1px solid rgba(255, 255, 255, 0.1);
      }

      &.btn--disabled {
        background: rgba(97, 133, 238, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
      }
    }
  }
</style>

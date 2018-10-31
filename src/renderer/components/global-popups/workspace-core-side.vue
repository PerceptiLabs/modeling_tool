<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      ul.popup_tab-set
        button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
        )
          h3(v-html="tab")
      .popup_tab-body
        .popup_body(
          :class="{'active': tabSelected == 0}"
        )
          .settings-layer_section.text-center
            p.big-text Start training
          .settings-layer_foot
            button.btn.btn--settings(type="button" @click="closePopup()") Cancel
            button.btn.btn--settings(type="button" @click="startTraining()") Start
        .popup_body(
          :class="{'active': tabSelected == 1}"
        )
          .settings-layer_section.text-center
            p.big-text this functionality is in development

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
export default {
  name: "SelectCoreSide",
  mixins: [mixinSet],
  data() {
    return {
      tabs: ['Computer', 'Cloud'],
      settings: {

      }
    }
  },
  computed: {

  },
  methods: {
    startTraining() {
      this.$store.commit('globalView/SET_appMode', 'training');
      this.closePopup();
    },
    closePopup() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
    }
  }
}
</script>

<style lang="scss" scoped>

</style>

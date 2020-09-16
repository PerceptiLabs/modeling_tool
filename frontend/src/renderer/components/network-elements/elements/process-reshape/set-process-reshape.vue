<template lang="pug">
  div
    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.reshape")
        .form_label Reshape:
        #tutorial_input-reshape.form_input(data-tutorial-hover-info)
          triple-input-element-reshape.tutorial-relative(
            v-model="settings.Shape"
            :axis-position="settings.Permutation"
            :validate-sum="currentEl.layerMeta.InputDim"
            @swap12="swap12"
            @swap23="swap23"
            @swap13="swap13"
            @handle-focus="setIsSettingInputFocused(true)"
            @handle-blur="setIsSettingInputFocused(false)"
            )

    .settings-layer_section
      .form_row(v-tooltip-interactive:right="interactiveInfo.reshape")
        .form_label Transpose map:
        .form_input
          setting-reshape-image(
            :axis-settings="settings.Shape"
          )
    
    //- sidebar-setting-preview(
    //-   :current-el="currentEl"
    //-   )
      //-.settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.transpose")
          .form_label Transpose:
          #tutorial_input-transpose.form_input(data-tutorial-hover-info)
            triple-input(v-model="settings.Permutation")

    //- template(slot="Code-content")
    //-   h1 (slot="Code-content"
    //-   settings-code(
    //-     :current-el="currentEl"
    //-     :el-settings="settings"
    //-     v-model="coreCode"
    //-   )
  //- settings-preview(
    //-   :current-el="currentEl"
    //- )
</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import mixinFocus     from '@/core/mixins/net-element-settings-input-focus.js';
  import TripleInput    from "@/components/base/triple-input";
  import TripleInputElementReshape    from "@/components/base/triple-input--element-reshape.vue";
  import SettingReshapeImage    from "@/components/network-elements/elements-settings/setting-reshape-image.vue";
  import SidebarSettingPreview  from "@/components/network-elements/elements-settings/sidebar-setting-preview.vue";
  import { mapActions, mapGetters } from 'vuex';

  export default {
    name: 'SetProcessReshape',
    mixins: [mixinSet, mixinFocus],
    components: { TripleInput, TripleInputElementReshape, SettingReshapeImage, SidebarSettingPreview },
    mounted() {
      this.$store.dispatch('mod_api/API_getInputDim');
      this.saveSettingsToStore("Settings");
    },
    data() {
      return {
        settings: {
          Shape: [28,28,1],
          Permutation: [0,1,2],
        },
        interactiveInfo: {
          reshape: {
            title: 'Reshape',
            text: 'Set the new shape of the data'
          },
          transpose: {
            title: 'Transpose',
            text: 'Change the axis positions of the data'
          }
        },
      }
    },
    computed: {
      ...mapGetters({
        isTutorialMode: 'mod_tutorials/getIsTutorialMode'
      }),
    },
    methods: {
      ...mapActions({
        infoPopup:                'globalView/GP_infoPopup',
      }),
      swap12() {
        const shap = this.settings.Shape;
        const perm = this.settings.Permutation;
        this.settings.Shape       = [shap[1], shap[0], shap[2]];
        this.settings.Permutation = [perm[1], perm[0], perm[2]];
      },
      swap23() {
        const shap = this.settings.Shape;
        const perm = this.settings.Permutation;
        this.settings.Shape       = [shap[0], shap[2], shap[1]];
        this.settings.Permutation = [perm[0], perm[2], perm[1]];
      },
      swap13() {
        const shap = this.settings.Shape;
        const perm = this.settings.Permutation;
        this.settings.Shape       = [shap[2], shap[1], shap[0]];
        this.settings.Permutation = [perm[2], perm[1], perm[0]];
      },
      // saveSettings(tabName) {
      //   console.log('[LOG]: saveSettings')
      //   console.trace();
      //   debugger;
      //   this.saveSettings('Settings');
      // },
    }
  }
</script>

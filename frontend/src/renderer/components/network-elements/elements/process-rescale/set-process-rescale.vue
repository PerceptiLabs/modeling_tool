<template lang="pug">
.settings-layer_section.rescale
  .form_row
    .form_label Width * Height:
    .form_input(style="padding-left: 0")
      input(
        style="width: 60px",
        type="number",
        v-model="settings.width",
        @focus="setIsSettingInputFocused(true)",
        @blur="setIsSettingInputFocused(false)",
        @keyup="changeWidth"
      )
    .form_input
      input(
        style="width: 60px",
        type="number",
        v-model="settings.height",
        @focus="setIsSettingInputFocused(true)",
        @blur="setIsSettingInputFocused(false)",
        @keyup="changeHeight"
      )
  button.btn.btn--icon.rescale-lock-button(
    type="button",
    :class="{ 'invisible-icon': !isLocked }",
    @click="toggleLock()"
  )
    svg(
      width="18",
      height="18",
      viewBox="0 0 18 18",
      fill="none",
      xmlns="http://www.w3.org/2000/svg"
    )
      path(
        d="M15 6.75H13.5V5.25C13.5 4.05653 13.0259 2.91193 12.182 2.06802C11.3381 1.22411 10.1935 0.75 9 0.75C7.80653 0.75 6.66193 1.22411 5.81802 2.06802C4.97411 2.91193 4.5 4.05653 4.5 5.25V6.75H3C2.80109 6.75 2.61032 6.82902 2.46967 6.96967C2.32902 7.11032 2.25 7.30109 2.25 7.5V16.5C2.25 16.6989 2.32902 16.8897 2.46967 17.0303C2.61032 17.171 2.80109 17.25 3 17.25H15C15.1989 17.25 15.3897 17.171 15.5303 17.0303C15.671 16.8897 15.75 16.6989 15.75 16.5V7.5C15.75 7.30109 15.671 7.11032 15.5303 6.96967C15.3897 6.82902 15.1989 6.75 15 6.75ZM6 5.25C6 4.45435 6.31607 3.69129 6.87868 3.12868C7.44129 2.56607 8.20435 2.25 9 2.25C9.79565 2.25 10.5587 2.56607 11.1213 3.12868C11.6839 3.69129 12 4.45435 12 5.25V6.75H6V5.25ZM9 14.25C8.55499 14.25 8.11998 14.118 7.74997 13.8708C7.37996 13.6236 7.09157 13.2722 6.92127 12.861C6.75097 12.4499 6.70642 11.9975 6.79323 11.561C6.88005 11.1246 7.09434 10.7237 7.40901 10.409C7.72368 10.0943 8.12459 9.88005 8.56105 9.79323C8.9975 9.70642 9.4499 9.75097 9.86104 9.92127C10.2722 10.0916 10.6236 10.38 10.8708 10.75C11.118 11.12 11.25 11.555 11.25 12C11.25 12.5967 11.0129 13.169 10.591 13.591C10.169 14.0129 9.59674 14.25 9 14.25Z",
        fill="#6185EE"
      )

  i.icon.multiple.icon-app-close
</template>

<script>
import mixinSet from "@/core/mixins/net-element-settings.js";
import mixinFocus from "@/core/mixins/net-element-settings-input-focus.js";
import { mapActions, mapGetters } from "vuex";

export default {
  name: "SetProcessRescale",
  mixins: [mixinSet, mixinFocus],
  mounted() {
    this.$store.dispatch("mod_api/API_getInputDim");
    this.saveSettingsToStore("Settings");
    if (this.currentEl.layerMeta.InputDim) {
      const dimention = this.currentEl.layerMeta.InputDim.split(",");
      const width = parseInt(dimention[0].slice(1));
      const height = parseInt(dimention[1].slice(1));

      this.ratio = height / width;
      this.settings.width = width;
      this.settings.height = height;
    }
  },
  data() {
    return {
      settings: {
        width: 40,
        height: 30,
      },
      isLocked: true,
      ratio: 0.75,
    };
  },
  methods: {
    changeWidth() {
      if (this.isLocked) {
        this.settings.height = parseInt(this.settings.width * this.ratio);
      }
    },
    changeHeight() {
      if (this.isLocked) {
        this.settings.width = parseInt(this.settings.height / this.ratio);
      }
    },
    saveSettings(tabName) {
      this.applySettings(tabName);
    },
    toggleLock() {
      this.isLocked = !this.isLocked;
      if (this.isLocked && this.settings.width > 0)
        this.ratio = this.settings.height / this.settings.width;
    },
  },
};
</script>

<style lang="scss">
.rescale-lock-button {
  &.invisible-icon {
    path {
      fill: $disable-txt;
    }
  }
}
.settings-layer_section.rescale {
  margin-top: 22px;
  position: relative;
}
.rescale-lock-button {
  position: absolute;
  top: -12px;
  right: 10px;
}
.multiple.icon-app-close {
  position: absolute;
  top: 18px;
  right: 31%;
  font-size: 6px;
}
</style>

const netElementSettingsInputFocus = {
  methods: {
    setIsSettingInputFocused(value) {
      this.$store.commit("mod_workspace/setIsSettingInputFocused", value);
    },
  }
};

export default netElementSettingsInputFocus


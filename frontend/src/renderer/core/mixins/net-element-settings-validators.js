const netElementSettingsValidators = {
  computed: {
    isValidKeepProbability() {
      const value = this.settings.Keep_prob;

      if (!value || value <= 0 || value > 1) {
        return false;
      } else {
        return true;
      }
    },
  }
};
  
export default netElementSettingsValidators;
  
  
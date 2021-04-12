const netElementSettingsValidators = {
  computed: {
    isValidKeepProbability() {
      const dropout =  this.settings.Dropout;
      const value = this.settings.Keep_prob;
      
      if(!dropout) { 
        return true;
      }
      
      if (!value || value <= 0 || value > 1) {
        return false;
      } else {
        return true;
      }
    },
  }
};
  
export default netElementSettingsValidators;
  
  
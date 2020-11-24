import { keyCloak } from '@/core/apiKeyCloak.js';

const namespaced = true;

const state = {
};

const getters = {

};

const mutations = {
};

const actions = {
  sendFirstLoginStatus(ctx, value = false) {
    const payload = { "attributes":
      {
        'firstlogin': value
      }
    };

    return new Promise((resolve, reject) => {
      return keyCloak.updateUserProfileAttributes({
        payload
      })
      .then(res => {
        resolve();
      });
    });
  },
  sendQuestionnaireResponses(ctx, answers) {

    const payload = { "attributes":
      {
        'firstlogin': false, // setting firstlogin because KC doesn't support PUT/PATCH
        'questionnaire': true,
        'questionnaire-responses': JSON.stringify(answers) 
      } // wraps it so it's a single object in KeyCloak
    };

    return new Promise((resolve, reject) => {
      return keyCloak.updateUserProfileAttributes({
        payload
      })
      .then(res => {
        resolve();
      });
    });
  },
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions,
}

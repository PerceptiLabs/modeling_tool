<template lang="pug">
  .user-profile
    base-switcher.sidebar_section(
      :tab-set-data="switcherData"
    )
      template(slot="firstTab")
        dl.user-info_list(v-if="user")
          dt.user-info_name First name
          dd.user-info_data
            text-editable(
              :text-title="user.firstName"
              @change-title="editFirstName"
              )
          dt.user-info_name Last name
          dd.user-info_data
            text-editable(
              :text-title="user.lastName"
              @change-title="editLastName"
            )
          dt.user-info_name Email
          dd.user-info_data(@dblclick="editEmail") {{ user.email }}

          form.user-info_edit-email(v-show="showEmailEditFields")
            .form_holder
              input(type="email" placeholder="New email"
                v-model="newEmail"
                name="new email"
                v-validate="'required|email'"
                ref="newEmail"
              )
              p.text-error(v-show="errors.has('new email') && newEmail") {{ errors.first('new email') }}

            .form_holder
              input(type="email" placeholder="Confirm new email"
                v-model="confirmNewEmail"
                name="confirm new email"
                v-validate="'required|confirmed:newEmail'"
              )
              p.text-error(v-show="errors.has('confirm new email') && confirmNewEmail") {{ errors.first('confirm new email') }}

      template(slot="secondTab")
        p secondTab
    .sidebar_action
      button.btn.btn--primary(type="button" @click="saveUserInfo") Save

</template>

<script>
import BaseSwitcher      from "@/components/different/switcher.vue";
import TextEditable      from '@/components/base/text-editable.vue'
import {requestCloudApi} from '@/core/apiCloud.js'


export default {
  name: "UserProfile",
  components: {BaseSwitcher, TextEditable},
  mounted() {
    if(!this.user) this.requestGetUserInfo();
  },
  data() {
    return {
      switcherData: ['User', 'History'],
      newEmail: '',
      confirmNewEmail: '',
      showEmailEditFields: false
    }
  },
  computed: {
    user() {
      return this.$store.getters['mod_user/GET_userProfile']
    }
  },
  methods: {
    requestCloudApi,
    editFirstName(newVal) {
      let newInfo = JSON.parse(JSON.stringify(this.user));
      newInfo.firstName = newVal;
      this.setUserInfo(newInfo);
    },
    editLastName(newVal) {
      let newInfo = JSON.parse(JSON.stringify(this.user));
      newInfo.lastName = newVal;
      this.setUserInfo(newInfo);
    },
    editEmail() {
      this.showEmailEditFields = !this.showEmailEditFields;
      this.newEmail = '';
      this.confirmNewEmail = '';
    },
    setUserInfo(userInfo) {
      this.$store.dispatch('mod_user/SET_userProfile', userInfo);
    },
    requestGetUserInfo() {
      this.requestCloudApi('get', 'Customer/Profile')
        .then((response) => {
          let responseUser = {
            firstName: response.data.data.firstName,
            lastName: response.data.data.lastName,
            email: response.data.data.email,
          };
          this.setUserInfo(responseUser);
        })
        .catch((error)=>{
          this.$store.dispatch('globalView/GP_infoPopup', error);
        })
    },
    saveUserInfo() {
      this.requestCloudApi('post', 'Customer/Profile', this.user)
        .then((response) => {
          this.$store.dispatch('globalView/GP_infoPopup', 'Your information has been changed');
        })
        .catch((error) => {
          this.$store.dispatch('globalView/GP_infoPopup', error);
        });
      if(this.showEmailEditFields && this.newEmail.length) {
        this.validateNewEmail()
          .then(() => this.requestChangeUserEmail())
          .then(() => {
            this.$store.dispatch('globalView/GP_infoPopup', `A confirmation has been sent to your old mail ${this.user.email}. Please follow the link and your mail will be changed. Otherwise, your old mail will act`);
            this.$store.dispatch('mod_events/EVENT_logOut');
          })
          .catch((error) => {
            this.$store.dispatch('globalView/GP_infoPopup', error);
          })
      }
    },
    requestChangeUserEmail() {
      let dataBody = {
        oldEmail: this.user.email,
        newEmail: this.newEmail,
        newEmailConfirmation: this.confirmNewEmail
      };
      return this.requestCloudApi('post', 'Customer/ChangeEmail', dataBody)
        .then((response) => {
          return response
        })
    },
    validateNewEmail() {
      return this.$validator.validateAll()
        .then((result) => {
          return result
        })
    },
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .user-info_list {
    font-size: 1.4rem;
    display: flex;
    flex-wrap: wrap;
  }
  .user-info_name {
    width: 40%;
    color: $disable-txt;
    margin-bottom: 1rem;
  }
  .user-info_data {
    width: 60%;
    margin: 0;
    margin-bottom: 1rem;
  }
  .sidebar_action {
    text-align: center;
  }
  .user-info_edit-email {
    width: 100%;
  }
</style>

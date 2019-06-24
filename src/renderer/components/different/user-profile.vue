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
              @change-title="editfirstName"
              )
          dt.user-info_name Last name
          dd.user-info_data
            text-editable(
              :text-title="user.lastName"
              @change-title="editlastName"
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
      button.btn.btn--primary(type="button" @click="requestChangeUserInfo") Save

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
      user: JSON.parse(localStorage.getItem('user')),
      newEmail: '',
      confirmNewEmail: '',
      showEmailEditFields: false
    }
  },
  computed: {
    // userInfo() {
    //   return [
    //     {dt: 'First name' ,dd:}
    //   ]
    // }
  },
  methods: {
    requestCloudApi,
    editfirstName(newVal) {
      this.user.firstName = newVal
    },
    editlastName(newVal) {
      this.user.lastName = newVal
    },
    editEmail() {
      this.showEmailEditFields = !this.showEmailEditFields;
      this.newEmail = '';
      this.confirmNewEmail = '';
    },
    requestGetUserInfo() {
      this.requestCloudApi('get', 'Customer/Profile')
        .then((response) => {
          this.user = {
            firstName: response.data.data.firstName,
            lastName: response.data.data.lastName,
            email: response.data.data.email,
          };
          localStorage.setItem('user', JSON.stringify(this.user));
        })
        .catch((error)=>{
          this.$store.dispatch('globalView/GP_infoPopup', error);
        })
    },
    requestChangeUserInfo() {
      let oldUserDate = JSON.parse(localStorage.getItem('user'));

      if(oldUserDate.firstName !== this.user.firstName || oldUserDate.lastName !== this.user.lastName) {
        localStorage.setItem('user', JSON.stringify(this.user));
        this.requestCloudApi('post', 'Customer/Profile', this.user)
          .then((response) => {
            this.$store.dispatch('globalView/GP_infoPopup', 'Your information has been changed');
          })
          .catch((error) => {
            this.$store.dispatch('globalView/GP_infoPopup', error);
          })
      }
      else {
        this.validateNewEmail()
      }
    },
    requestChangeUserEmail(newEmailInfo) {
      this.requestCloudApi('post', 'Customer/ChangeEmail', newEmailInfo)
        .then((response) => {
          console.log(response)
        })
        .catch((error) => {
          this.$store.dispatch('globalView/GP_infoPopup', error);
        })
    },
    validateNewEmail() {
      let newEmailInfo = {
        oldEmail: this.user.email,
        newEmail: this.newEmail,
        newEmailConfirmation: this.confirmNewEmail
      };
      this.$validator.validateAll()
        .then((result) => {
          if (result) {
            this.requestChangeUserEmail(newEmailInfo);
            this.showEmailEditFields = false;
            this.$store.dispatch('globalView/GP_infoPopup', `A confirmation has been sent to your old mail ${this.user.email}. Please follow the link and your mail will be changed. Otherwise, your old mail will act`);
            this.$store.dispatch('mod_events/EVENT_logOut', this);
            return;
          }
          //error func
        })
        .catch((error)=>{
          console.log('error', error);
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

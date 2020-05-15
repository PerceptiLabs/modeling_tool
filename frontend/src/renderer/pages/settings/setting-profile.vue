<template lang="pug">
  div(v-if="user")
    .contnet-caption Review your personal information here
    .profile-box
      .profile-preview {{user && user.firstName[0]}}
      .input-wrapper
        label(for="name") First Name
        .form_row
          input(id="name" type="text" :value="user.firstName")
      .input-wrapper
        label(for="name") Last Name
        .form_row
          input(id="name" type="text" :value="user.lastName")
      .input-wrapper
        label(for="email") Email
        .form_row
          input(id="email" type="text" :value="user.email")
      .input-wrapper
        label(for="email") Password
        p.password-star ***************
        button.change-password-btn(
          @click="handleDisplayPasswordModal(true)"
        ) Change pasword

      .change-password-actions
        button.change-password-modal-btn.blue() Save
        button.change-password-modal-btn(@click="resetChangedValues") Cancel

    div(v-if="isChangePasswordOpened")
      div.popup-new-ui 
        div.popup-new-ui-header Change password
        div.popup-new-ui-content
          form.user-info_edit(
              data-vv-scope="formPassword"
            )
            .form_row
              input(
                type="password"
                name="password"
                v-validate="'required'"
                placeholder='Current password'
                v-model="password.oldPassword")
            p.text-error(
              v-show="errors.has('formPassword.password')") {{ errors.first('formPassword.password') }}
            br
            .form_row
              input(
                type="password"
                name="new password"
                v-validate="{required: true, min: 6, is_not: password.oldPassword}"
                placeholder="New password"
                v-model="password.newPassword"
                ref="userPass")
            p.text-error(
              v-show="errors.has('formPassword.new password')") {{ errors.first('formPassword.new password') }}
            br
            .form_row
              input(type="password"
              name="confirm new password"
              v-validate="'required|confirmed:userPass'"
              data-vv-as="new password"
              placeholder="Repeat new password"
              v-model="password.newPasswordConfirmation")
            p.text-error(
              v-show="errors.has('formPassword.confirm new password')") {{ errors.first('formPassword.confirm new password') }}

            .change-password-actions
              button.change-password-modal-btn.blue(@click.prevent="handleSavePassword") Save
              button.change-password-modal-btn(@click="handleDisplayPasswordModal(false)") Cancel
          
</template>
<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'SettingProfile',
  data() {
    return {
      isChangePasswordOpened: false,
      password: {
        oldPassword: '',
        newPassword: '',
        newPasswordConfirmation: '',
      }
    }
  },
  computed: {
    ...mapGetters({
      user: 'mod_user/GET_userProfile',
    })
  },
  methods: {
    ...mapActions({
      showInfoPopup:            'globalView/GP_infoPopup',
      showErrorPopup:           'globalView/GP_errorPopup',
      setUserInfo:              'mod_user/SET_userProfile',
      logout:                   'mod_events/EVENT_logOut',
      cloud_userGetProfile:     'mod_apiCloud/CloudAPI_userGetProfile',
      cloud_userSetProfile:     'mod_apiCloud/CloudAPI_userSetProfile',
      cloud_userChangeEmail:    'mod_apiCloud/CloudAPI_userChangeEmail',
      cloud_userChangePassword: 'mod_apiCloud/CloudAPI_userChangePassword',
    }),
    handleDisplayPasswordModal(value) {
      this.isChangePasswordOpened = value;
    },
    resetChangedValues() {

    },
    handleSavePassword() {
      this.validateForm('formPassword')
       .then((isValid)=> {
          if(isValid) {
            return this.cloud_userChangePassword(this.password)
          }
        })
        .then((res)=> {
          this.password.oldPassword = '';
          this.password.newPassword = '';
          this.password.newPasswordConfirmation = '';
          this.handleDisplayPasswordModal(false);
          this.showInfoPopup('A new password has been changed');
          return 'A new password has been changed'
        })
    },
    validateForm(scope) {
      return this.$validator.validateAll(scope)
        .then((result) => {
          return result 
        })
    },
    
  }
}
</script>
<style lang="scss" scoped>

.contnet-caption {
  font-family: Nunito Sans;
  font-size: 16px;
  line-height: 22px;
  color: #C4C4C4;
}
.profile-box {
  width: 365px;
  margin-top: 17px;
  padding: 35px 40px 30px 30px;
  border: 1px solid #4D556A;
  border-radius: 2px;
}
.profile-preview {
  width: 60px;
  height: 60px;
  margin-bottom: 32px;
  background: #EE6161;
  border-radius: 50%;
  text-align: center;
  line-height: 60px;
  font-family: Nunito Sans;
  font-weight: bold;
  font-size: 30px;
  color: #FFFFFF;
}
.input-wrapper {
  margin-bottom: 20px;
  label {
    display: inline-block;
    margin-bottom: 8px;
    font-family: Nunito Sans;
    font-size: 16px;
    line-height: 22px;
    color: #9E9E9E;
  }
}
.password-star {
  margin-bottom: 0px;
  font-family: Nunito Sans;
  font-weight: 600;
  font-size: 16px;
  line-height: 22px;
  color: #C4C4C4
}
.change-password-btn {
  font-family: Nunito Sans;
  font-size: 14px;
  line-height: 19px;
  letter-spacing: 0.05em;
  color: #9BB2F6;
  background: none;
  padding: 0;
  margin: 0;
}
.change-password-actions {
  display: flex;
  flex-direction: row-reverse;
  margin-top: 24px;
}
.change-password-modal-btn {
  height: 30px;
  min-width: 95px;
  background: rgba(97, 133, 238, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-sizing: border-box;
  border-radius: 2px;

  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 600;
  font-size: 14px;
  line-height: 19px;

  color: #FFFFFF;

  &.blue {
    margin-left: 10px;
    background: #6185EE;
  }
}
</style>
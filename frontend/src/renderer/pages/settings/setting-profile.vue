<template lang="pug">
  div(v-if="user")
    .contnet-caption Review your personal information here
    .profile-box
      .profile-preview {{user && user.firstName[0]}}
      form(
        data-vv-scope="userNames"
      )
        .input-wrapper
          label(for="name") First Name
          .form_row
            input(id="name" name="firstName" v-validate="'required|min:3'" type="text" @input="editFirstName" :value="user.firstName" )
          p.text-error(
              v-show="errors.has('userNames.firstName')") {{ errors.first('userNames.firstName') }}   
        .input-wrapper
          label(for="last_name") Last Name
          .form_row
            input(id="last_name" name="lastName" v-validate="'required|min:3'" type="text" @input="editLastName" :value="user.lastName")
          p.text-error(
              v-show="errors.has('userNames.lastName')") {{ errors.first('userNames.lastName') }}   
      form(
        data-vv-scope="formEmail"
      )
        .input-wrapper
          label Email
          .form_row
            input.email-disabled(@input="editEmail" name="new email" disabled readonly v-validate="'required|email'"  type="text" :value="user.email" )
          p.text-error(
              v-show="errors.has('formEmail.new email')") {{ errors.first('formEmail.new email') }}    
      .input-wrapper
        label() Password
        p.password-star ***************
        button.change-password-btn(
          @click="handleDisplayPasswordModal(true)"
        ) Change pasword

      .change-password-actions
        button.change-password-modal-btn.blue(@click="handleSaveProfile") Save
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
import { deepCopy } from "@/core/helpers.js";
export default {
  name: 'SettingProfile',
  data() {
    return {
      isChangePasswordOpened: false,
      userData: {
        firstName: '',
        lastName: '',
        email: '',
      },
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
  beforeDestroy() {
     document.removeEventListener('click', this.closePasswordModal, true)
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
      if(!value) {
      this.$validator.pause();
        document.removeEventListener('click', this.closePasswordModal, true)
      }
      else {
        this.$validator.resume();
        document.addEventListener('click', this.closePasswordModal, true)
      }
      this.isChangePasswordOpened = value;
    },
    closePasswordModal(e) {
      const classArray = [
        e.target.parentElement.className,
        e.target.parentElement.parentElement.className,
        e.target.parentElement.parentElement.parentElement.className,
        e.target.parentElement.parentElement.parentElement.parentElement.className,
        e.target.parentElement.parentElement.parentElement.parentElement.parentElement.className,
      ]
      if(classArray.indexOf('popup-new-ui') === -1) {
        this.handleDisplayPasswordModal(false);
      }
    },
    
    resetChangedValues() {
      this.cloud_userGetProfile();
    },
    handleSavePassword() {
      this.validateForm('formPassword')
       .then((isValid)=> {
          if(isValid) {
            return this.cloud_userChangePassword(this.password)
          }
          return isValid
        })
        .then((isValid)=> {
          if(!isValid)
          return;

          this.password.oldPassword = '';
          this.password.newPassword = '';
          this.password.newPasswordConfirmation = '';
          this.handleDisplayPasswordModal(false);
          this.showInfoPopup('Your password has been changed');
          return 'Your password has been changed'
        })
    },
    handleSaveProfile(){
      this.validateForm('userNames')
        .then(isValid => {
          if(isValid) {
            this.cloud_userSetProfile(this.user)
              .then(res => {
                this.showInfoPopup('Your user name has been changed');
              })
          }
        });

      
    },
    editFirstName(e) {
      let newInfo = deepCopy(this.user);
      newInfo.firstName = e.target.value;
      this.setUserInfo(newInfo);
    },
    editLastName(e) {
      let newInfo = deepCopy(this.user);
      newInfo.lastName = e.target.value;
      this.setUserInfo(newInfo);
    },
    editEmail(e) {
    //  let newInfo = deepCopy(this.user);
    //   newInfo.email = e.target.value;
    //   this.setUserInfo(newInfo);
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
.email-disabled {
    background: #4B4D52;
    opacity: 0.7;
  }
</style>

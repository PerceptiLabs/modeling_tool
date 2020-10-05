<template lang="pug">
  .user-profile(v-if="user")
    //-base-switcher.sidebar_section(
      /:tab-set-data="switcherData"
      )
      template(slot="firstTab")
        p first tab

      template(slot="secondTab")
        p secondTab
    .sidebar_section
      ul.user-info_list
        li
          .user-info_name First name
          .user-info_data
            text-editable(
              :text-title="user.firstName"
              @change-title="editFirstName"
            )
        li
          .user-info_name Last name
          .user-info_data
            text-editable(
              :text-title="user.lastName"
              @change-title="editLastName"
            )
        li
          .user-info_name Email
          .user-info_data(@dblclick="toggleEmailForm") {{ user.email }}
          form.user-info_edit(
            v-show="isShowEmailForm"
            data-vv-scope="formEmail"
          )
            .form_holder
              input(type="email" placeholder="New email"
                v-model="email.newEmail"
                name="new email"
                v-validate="'required|email'"
                ref="newEmail"
              )
              p.text-error(
                v-show="errors.has('formEmail.new email')"
              ) {{ errors.first('formEmail.new email') }}

            .form_holder
              input(type="email" placeholder="Confirm new email"
                v-model="email.newEmailConfirm"
                name="confirm new email"
                v-validate="'required|confirmed:newEmail'"
              )
              p.text-error(
                v-show="errors.has('formEmail.confirm new email')"
              ) {{ errors.first('formEmail.confirm new email') }}
        li
          .user-info_name Password
          .user-info_data(@dblclick="togglePasswordForm") {{ userPassword }}
          form.user-info_edit(
            v-show="isShowPasswordForm"
            data-vv-scope="formPassword"
          )
            .form_holder
              input(type="password" placeholder="Current password"
                v-model="password.oldPassword"
                name="password"
                v-validate="'required'"
              )
              p.text-error(
                v-show="errors.has('formPassword.password')"
              ) {{ errors.first('formPassword.password') }}
            .form_holder
              input(type="password" placeholder="New password"
                v-model="password.newPassword"
                name="new password"
                v-validate="{required: true, min: 6, is_not: password.oldPassword}"
                ref="userPass"
              )
              p.text-error(
                v-show="errors.has('formPassword.new password')"
              ) {{ errors.first('formPassword.new password') }}

            .form_holder
              input(type="password" placeholder="Confirm new password"
                v-model="password.newPasswordConfirmation"
                name="confirm new email"
                v-validate="'required|confirmed:userPass'"
                data-vv-as="new password"
              )
              p.text-error(
                v-show="errors.has('formPassword.confirm new email')"
              ) {{ errors.first('formPassword.confirm new email') }}
    .sidebar_action
      button.btn.btn--link(type="button"
        @click="saveUserInfo"
        :disabled="isDisabledBtn") Save

</template>

<script>
import BaseSwitcher from "@/components/different/switcher.vue";
import TextEditable from '@/components/base/text-editable.vue'

import { mapGetters, mapMutations, mapActions } from 'vuex';
import { deepCopy } from "@/core/helpers.js";

export default {
  name: "UserProfile",
  components: {BaseSwitcher, TextEditable},
  mounted() {
    if(!this.user) this.cloud_userGetProfile();
  },
  data() {
    return {
      switcherData: ['User', 'History'],
      isShowEmailForm: false,
      isShowPasswordForm: false,
      isDisabledBtn: false,
      userPassword: '******',
      email: {
        newEmail: '',
        newEmailConfirm: '',
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
      user: 'mod_user/GET_userProfile'
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
    editFirstName(newVal) {
      let newInfo = deepCopy(this.user);
      newInfo.firstName = newVal;
      this.setUserInfo(newInfo);
    },
    editLastName(newVal) {
      let newInfo = deepCopy(this.user);
      newInfo.lastName = newVal;
      this.setUserInfo(newInfo);
    },
    toggleEmailForm() {
      this.isShowEmailForm = !this.isShowEmailForm;
      this.email = {
        newEmail: '',
        newEmailConfirm: '',
      }
    },
    togglePasswordForm() {
      this.isShowPasswordForm = !this.isShowPasswordForm;
      this.password = {
        oldPassword: '',
        newPassword: '',
        newPasswordConfirmation: '',
      };
    },
    saveUserInfo() {
      Promise.all([ changeProfile(this), changeEmail(this), changePassword(this) ])
        .then((result)=> {
          let listInfo = [];
          let emailValidation = result[1];
          let passValidation = result[2];
          if(emailValidation || passValidation) {
            result.forEach((el)=> { if(el) listInfo.push(el) });
            this.showInfoPopup(listInfo);
          }
        })
        .catch((error) => {
          console.log(error)
        });


      function changeProfile(ctx) {
        return ctx.cloud_userSetProfile(ctx.user)
          .then(()=> {
            return 'Your information has been changed'
          });
      }
      function changeEmail(ctx) {
        if(ctx.isShowEmailForm && ctx.email.newEmail.length) {
          return ctx.validateForm('formEmail')
            .then((isValid)=> {
              if(isValid) {
                const request = {
                  oldEmail: ctx.user.email,
                  newEmail: ctx.email.newEmail,
                  newEmailConfirmation: ctx.email.newEmailConfirm
                };
                return ctx.cloud_userChangeEmail(request)
              }
              else {
                return false;
              }
            })
            .then((isValid)=> {
              if (isValid) {
                ctx.logout();
                return `A confirmation has been sent to your existing address at ${ctx.user.email}. Please follow the link in that email to change your address.`;
              }
              else {
                return false;
              }
            })
        }
      }
      function changePassword(ctx) {
        if(ctx.isShowPasswordForm && ctx.password.newPassword.length) {
          return ctx.validateForm('formPassword')
            .then((isValid)=> {
              if(isValid) {
                return ctx.cloud_userChangePassword(ctx.password)
              }
            })
            .then(()=> {
              return 'Your password has been changed'
            })
        }
      }
    },
    validateForm(scope) {
      return this.$validator.validateAll(scope)
        .then((result) => result )
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .user-info_list {
    font-size: 1.4rem;
    > li {
      display: flex;
      flex-wrap: wrap;
    }
  }
  .user-info_name {
    display: inline-block;
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
    text-align: right;
  }
  .user-info_edit {
    width: 100%;
  }
</style>

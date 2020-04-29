<template lang="pug">
  logout-user-page-wrap(
    title-page="Log in"
  )
    form.login_form(@keyup.enter="validateForm")
      .form_holder
        input(type="email" placeholder="Email"
          v-model="userEmail"
          name="Email"
          v-validate="'required|email'"
        )
        p.text-error(v-show="errors.has('Email')") {{ errors.first('Email') }}
      .form_holder
        .relative
          input(
            :type="passwordVisibility.password ? 'text' : 'password'"
            placeholder="Password"
            v-model="userPass"
            name="Password"
            v-validate="'required|min:6'"
          )
          img.show-hide-password-icon(
            src="../../../../static/img/inputs/show-hide.png"
            alt="show-hide-password"
            @click="togglePasswordVisibility('password')"
          )
        p.text-error(v-show="errors.has('Password')") {{ errors.first('Password') }}
        .forgot-password-box
          a.btn.btn--link-without-underline(
            :href="`${baseUrlSite}/restore-account`"
            @click.prevent="setActivePageAction(MODAL_PAGE_RESTORE_ACCOUNT)"
          ) Forgot password?
        base-checkbox.remember-me(v-model="saveToken")
          span.fz-16 Remember me
    .form_holder.login-form_actions
      .form_row
        button.btn.btn--dark-blue-rev.log-in-btn(type="button" @click="validateForm" :disabled="isLoading") Log in
    .form_holder.fz-16.italic.text-left
      span Don't have an account? 
      button.btn.btn--link(@click="setActivePageAction(MODAL_PAGE_SIGN_UP)" type="submit") Register here
</template>

<script>
  import { googleAnalytics } from '@/core/analytics';
  import { baseUrlSite }    from '@/core/constants.js'
  import { goToLink, encryptionData, isWeb }       from '@/core/helpers.js'
  
  import LogoutUserPageWrap from '@/pages/logout-user-page-wrap.vue'
  import {mapActions} from "vuex";
  import {MODAL_PAGE_SIGN_UP, MODAL_PAGE_RESTORE_ACCOUNT, MODAL_PAGE_PROJECT} from "@/core/constants";
export default {
  name: 'PageLogin',
  components: { LogoutUserPageWrap },
  data() {
    return {
      userEmail: '',
      userPass: '',
      saveToken: true,
      baseUrlSite,
      passwordVisibility: {
        password: false,
      },
      isWeb: isWeb(),
      MODAL_PAGE_SIGN_UP,
      MODAL_PAGE_RESTORE_ACCOUNT,
    }
  },
  computed: {
    isLoading() {
      return this.$store.state.mod_login.showLoader
    },
  },
  methods: {
    ...mapActions({
      setActivePageAction: 'modal_pages/setActivePageAction',
      closeActivePageAction: 'modal_pages/closePageAction',
    }),
    togglePasswordVisibility(fieldName) {
      this.passwordVisibility[fieldName] = !this.passwordVisibility[fieldName];
    },
    toLink(url) {
      goToLink(url)
    },
    validateForm() {
      this.$validator.validateAll()
        .then((result)=> {
          if (result) {
            this.requestLoginUser();
            return;
          }
      });
    },
    requestLoginUser() {
      googleAnalytics.trackCustomEvent('login');
      this.$store.commit('mod_login/SET_showLoader', true);
      let dataParams = {
        "Email": this.userEmail,
        "Password": this.userPass
      };
      this.$store.dispatch('mod_apiCloud/CloudAPI_userLogin', dataParams)
        .then((tokens)=> {
          if(tokens) {
            if(isWeb()) {
              this.$store.dispatch('mod_user/SET_userTokenSession', tokens);
            }
            if(this.saveToken) {
              this.$store.dispatch('mod_user/SET_userTokenLocal', tokens);
            }
            if(isWeb()) {
              this.$store.dispatch('mod_api/API_setUserInCore');
            }
            
            this.setActivePageAction(MODAL_PAGE_PROJECT);
            this.$router.push({name: 'projects'});
          }
        })
        .catch((error)=> {console.log(error)})
        .finally(()=>    {this.$store.commit('mod_login/SET_showLoader', false)});
    },
  }
}
</script>
<style lang="scss" scoped>
  .forgot-password-box{
    margin-top: 1rem;
    text-align: left;
  }
  .login_form {
    padding-top: 30px;
  }
  .remember-me {
    float: left;
    color: #fff;
    .checkbox-text {
      font-size: 16px !important; 
    }
  }
  .remember-me {
    margin-top: 15px;
  }
  .fz-16 {
    font-size: 16px;
  }
  .log-in-btn {
    width: 100%;
    height: 35px;
    font-weight: bold;
    font-size: 16px;
  }
  .italic {
    font-style: italic;
  }
  .btn--link {
    color: #6E92FA;
    &:hover {
      text-decoration: underline;
    }
  }
  .text-left {
    text-align: left;
  }
  .relative {
    position: relative;
  }
  .show-hide-password-icon {
    cursor: pointer;
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
  }
</style>

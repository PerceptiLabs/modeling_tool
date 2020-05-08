<template lang="pug">
  div.wrapper
    view-loading
    form(@keyup.enter="validateForm")
      img.site-logo(src="./../../../../static/img/perceptilabs-new-log.svg")

      .form_holder
        input.new-ui(type="email" placeholder="Email"
          v-model="userEmail"
          name="Email"
          v-validate="'required|email'"
        )
        p.text-error(v-show="errors.has('Email')") {{ errors.first('Email') }}
      .form_holder
        .relative
          input.new-ui(
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
        div.remember-and-forgot-section
          base-checkbox(:isNewUi="true").remember-me(v-model="saveToken")
            span.fz-12 Remember me
          .forgot-password-box
            a.btn.btn--link-without-underline.fz-12(
              :href="`${baseUrlSite}/restore-account`"
              @click.prevent="setActivePageAction(MODAL_PAGE_RESTORE_ACCOUNT)"
            ) Forgot password?
    .form_holder
      .form_row
        button.btn.btn--dark-blue-rev.log-in-btn(type="button" @click="validateForm" :disabled="isLoading") Log in
    .form_holder.fz-12.text-center
      span Don't have an account? 
      button.btn.btn--link(@click="setActivePageAction(MODAL_PAGE_SIGN_UP)" type="submit") Sign up here
</template>

<script>
  import { googleAnalytics } from '@/core/analytics';
  import { baseUrlSite }    from '@/core/constants.js'
  import { goToLink, encryptionData, isWeb }       from '@/core/helpers.js'
  
  import LogoutUserPageWrap from '@/pages/logout-user-page-wrap.vue'
  import {mapActions} from "vuex";
  import {MODAL_PAGE_SIGN_UP, MODAL_PAGE_RESTORE_ACCOUNT, MODAL_PAGE_PROJECT} from "@/core/constants";
  import ViewLoading from '@/components/different/view-loading.vue'
export default {
  name: 'PageLogin',
  components: { LogoutUserPageWrap, ViewLoading },
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
      closePageAction: 'modal_pages/closePageAction',
      closeActivePageAction: 'modal_pages/closePageAction',
      cloud_userGetProfile:     'mod_apiCloud/CloudAPI_userGetProfile',
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
            
            this.cloud_userGetProfile();
            // call this if haven't project setted in local storage
            const hasProjectSelected = localStorage.hasOwnProperty('targetProject');
            if(!hasProjectSelected) {
              this.setActivePageAction(MODAL_PAGE_PROJECT);
            } else {
              this.closePageAction();
            }
            if(this.$router.name !== 'projects')
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
  * {
    font-family: "Nunito Sans"
  }
  .wrapper {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: linear-gradient(-45deg, #383F50 0%, #23252A 100%);
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
    border-radius: 2px;
    width: 687px;
    padding: 100px 195px 115px;
  }

  .site-logo {
    margin: 0 auto 40px;
    display: block
  }

  // input[type=email], input[type=password], input[type=text] {
  //   background: #383F50;
  //   border: 1px solid #4B4D52;
  //   box-sizing: border-box;
  //   border-radius: 20px;
  //   height: 40px;
  //   padding-left: 20px;
  //   padding-right: 20px;

  //   font-family: Nunito Sans;
  //   font-style: normal;
  //   font-weight: 300;
  //   font-size: 12px;
  //   line-height: 16px;

  //   color: #fff;

  //   &::placeholder {
  //     color: #C4C4C4;
  //   }
  //   &:focus {
  //     border: 1px solid #6185EE;
  //   }
  // }

  .log-in-btn {
    background: #6185EE;
    border-radius: 20px;
    &:hover {
      color: #fff;
    }
  }

  .text-error {
    margin-top: 4px;
    padding-left: 20px;
    padding-right: 20px;
    font-size: 12px;
    text-align: center;
  }

  .remember-and-forgot-section {
    display: flex;
    justify-content: space-between;
    padding: 0 15px;
    margin-top: 10px;
    margin-bottom: 24px;
  }
  .forgot-password-box{
    // margin-top: 1rem;
    a {
      color: #9BB2F6;
    }
  }
  .custom-checkbox .checkbox-fake {
    flex: 0 0 13px;
    width: 13px;
    height: 13px;
  }
  .remember-me {
    color: #fff;
  }
  .fz-16 {
    font-size: 16px;
  }
  .log-in-btn {
    width: 100%;
    height: 35px;
    font-weight: bold;
    font-size: 14px;
  }
  .italic {
    font-style: italic;
  }
  .btn--link {
    color: #9BB2F6;
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

  .fz-12 {
    font-size: 12px;
  }
</style>


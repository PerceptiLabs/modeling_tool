<template lang="pug">
  logout-user-page-wrap.page_login(
    title-page="Account Recovery"
  )
    form.login_form(@keyup.enter="validateForm")
      template(v-if="success")
        .form_holder
          input(type="email" placeholder="Email"
            v-model="user.email"
            name="Email"
            v-validate="'required|email'"
            )
          p.text-error(v-show="errors.has('Email')") {{ errors.first('Email') }}

        .form_holder.login-form_actions
          .form_row
            span
            button.btn.btn--dark-blue-rev(type="button"
              @click="validateForm"
              :disabled="isLoading"
              ) Restore
      template(v-else)
        .form_holder
          p.big-text Please check your email!

      .form_holder
        router-link.btn.btn--link(:to="{name: 'login'}") Login

</template>

<script>
  import LogoutUserPageWrap from '@/pages/logout-user-page-wrap.vue'

export default {
  name: 'PageRestoreAccount',
  components: { LogoutUserPageWrap },
  data() {
    return {
      user: {
        email: '',
      },
      success: true,
    }
  },
  computed: {
    isLoading() {
      return this.$store.state.mod_login.showLoader
    },
  },
  methods: {
    validateForm() {
      this.$validator.validateAll()
        .then((result) => {
          if (result) {
            this.registryUser();
            return;
          }
        })
        .catch((error)=> {
          console.log('error', error);
        })
    },
    registryUser() {
      this.$store.commit('mod_login/SET_showLoader', true);

      this.$store.dispatch('mod_apiCloud/CloudAPI_userForgotPassword', this.user.email)
        .then((response)=> {
          this.success = false;
          //this.$router.replace('/login')
        })
        .catch((err)=> {
          console.log(err)
        })
        .finally(()=> this.$store.commit('mod_login/SET_showLoader', false));
    },
    toPolicy() {
      this.isShowPolicy = true;
    },
    toRegister() {
      this.isShowPolicy = false;
    },
  }
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';
  .policy-btn {
    margin-left: .3em;
  }
</style>

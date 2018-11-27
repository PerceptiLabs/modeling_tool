<template lang="pug">
  main.page_login
    .login_logo
      img(src="~@/assets/percepti-labs-logo.svg" alt="percepti labs logo")
    .login_main
      h1 Get Started
      h3 Register in 1 minute
      form.login_form
        .form_holder
          input(type="text"     placeholder="First Name"  name="First Name" v-validate="'alpha_spaces'" )
          p.text-error(v-show="errors.has('First Name')") {{ errors.first('First Name') }}
        .form_holder
          input(type="text"     placeholder="Last Name"   name="Last Name"  v-validate="'alpha_spaces'" )
          p.text-error(v-show="errors.has('First Name')") {{ errors.first('First Name') }}
        .form_holder
          input(type="tel"     placeholder="Phone"        name="Phone"      v-mask="'+## (###) ###-##-##'")
        .form_holder
          input(type="email"    placeholder="Email"       name="Email"      v-validate="'required|email'" )
          p.text-error(v-show="errors.has('Email')") {{ errors.first('Email') }}
        .form_holder
          input(type="password" placeholder="Password"    name="Password"   v-validate="'required|min:6'" ref="userPass")
          p.text-error(v-show="errors.has('Password')") {{ errors.first('Password') }}
        .form_holder
          input(type="password" placeholder="Confirm password"
            name="Confirm password"
            v-validate="'required|confirmed:userPass'"
            data-vv-as="Password"
            )
          p.text-error(v-show="errors.has('Confirm password')") {{ errors.first('Confirm password') }}
        .form_holder
          base-checkbox(name="terms" v-validate="'required'"

          )
            span Agree
            router-link(:to="{name: 'policy'}").btn.btn--link  terms and policy
          p.text-error(v-show="errors.has('terms')") {{ errors.first('terms') }}
        .form_holder
          button.btn.btn--dark-blue-rev(type="button" @click="validateForm") log in
        .form_holder
          router-link(:to="{name: 'login'}").btn.btn--link Already Have Account
</template>

<script>
export default {
  name: 'PageRegister',
  methods: {
    validateForm() {
      this.$validator.validateAll()
        .then((result) => {
          if (result) {
            this.registryUser();
            return;
          }
          //error func
        });
    },
    registryUser() {
      alert('loginUser');
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';

</style>

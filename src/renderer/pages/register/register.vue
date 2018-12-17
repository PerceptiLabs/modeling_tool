<template lang="pug">
  main.page_login
    .login_logo
      img(src="~@/assets/percepti-labs-logo.svg" alt="percepti labs logo")
    .login_main
      h1 Get Started
      h3 Register in 1 minute
      form.login_form
        .form_holder
          input(type="text" placeholder="First Name"
            v-model="user.firstName"
            name="First Name"
            v-validate="'alpha_spaces'"
            )
          p.text-error(v-show="errors.has('First Name')") {{ errors.first('First Name') }}
        .form_holder
          input(type="text" placeholder="Last Name"
            v-model="user.lastName"
            name="Last Name"
            v-validate="'alpha_spaces'"
            )
          p.text-error(v-show="errors.has('First Name')") {{ errors.first('First Name') }}
        .form_holder
          input(type="tel" placeholder="Phone"
            v-model="user.phone"
            name="Phone"
            v-mask="'+## (###) ###-##-##'"
            )
        .form_holder
          input(type="email" placeholder="Email"
            v-model="user.email"
            name="Email"
            v-validate="'required|email'"
            )
          p.text-error(v-show="errors.has('Email')") {{ errors.first('Email') }}
        .form_holder
          input(type="password" placeholder="Password"
            v-model="user.password"
            name="Password"
            v-validate="'required|min:6'"
            ref="userPass")
          p.text-error(v-show="errors.has('Password')") {{ errors.first('Password') }}
        .form_holder
          input(type="password" placeholder="Confirm password"
            name="Confirm password"
            v-validate="'required|confirmed:userPass'"
            data-vv-as="Password"
            )
          p.text-error(v-show="errors.has('Confirm password')") {{ errors.first('Confirm password') }}
        .form_holder
          base-checkbox(
            validateName="policy"
            v-model="terms"
          )
            span Agree
            router-link(:to="{name: 'policy'}").btn.btn--link  terms and policy

        .form_holder
          button.btn.btn--dark-blue-rev(type="button" @click="validateForm") Register
        .form_holder
          router-link(:to="{name: 'login'}").btn.btn--link Already Have Account
</template>

<script>
  import {requestCloudApi} from '@/core/apiCloud.js'
export default {
  name: 'PageRegister',
  data() {
    return {
      user: {
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        password: ''
      },
      terms: true
    }
  },
  methods: {
    requestCloudApi,
    validateForm() {
      if(!this.terms) {
        return
      }
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
      console.log('registryUser');
      this.requestCloudApi('post', 'Customer/CreateGuest', this.user, (result, response, error) => {
        if (result === 'success') {
          console.log(response);
          alert('authorization success');
          this.$router.replace('/login');
        }
        else {
          console.log(error);
          alert(error.Message);
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';

</style>

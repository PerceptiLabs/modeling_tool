<template lang="pug">
  .page_login
    .login_logo
      img(src="~@/assets/percepti-labs-logo.svg" alt="percepti labs logo")
    .login_main
      h1 Get Started
      h3 Register in 1 minute
      form.login_form
        .form_holder
          input(type="text" placeholder="First and Last Name")
        .form_holder
          input(type="email" placeholder="Email")
        .form_holder
          input(type="password" placeholder="Password")
        .form_holder
          base-checkbox(

          )  
            span Agree 
            router-link(:to="{name: 'policy'}").btn.btn--link  terms and policy
        .form_holder
          button.btn.btn--dark-blue-rev(type="button") log in
        .form_holder
          router-link(:to="{name: 'login'}").btn.btn--link Already Have Account
</template>

<script>
export default {
  name: 'PageRegister'
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';

</style>

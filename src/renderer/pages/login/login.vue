<template lang="pug">
  .page_login
    .login_logo
      img(src="~@/assets/percepti-labs-logo.svg" alt="percepti labs logo")
    .login_main
      h1 Log In please
      h3 Enter your Email & Password
      form.login_form
        .form_holder
          input(type="email" placeholder="Email")
        .form_holder
          input(type="password" placeholder="Password")
        .form_holder
          base-checkbox(

          ) Remember me
        .form_holder
          router-link.btn.btn--dark-blue-rev(type="button" :to="{name: 'app'}") log in
        .form_holder
          router-link(:to="{name: 'register'}").btn.btn--link Register new account
</template>

<script>
export default {
  name: 'PageLogin'
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';

</style>

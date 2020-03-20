<template lang="pug">
  div.wrapper
    router-link.nav-link(
      :to="{name: 'app'}")
      img(src="../../../../static/img/project-page/file.svg")
    router-link.nav-link.is-active(
      :to="{name: 'app'}")
      img(src="../../../../static/img/project-page/search.svg")
    router-link.nav-link(
      :to="{name: 'app'}")
      img(src="../../../../static/img/project-page/repository.svg")
    router-link.nav-link(
      :to="{name: 'app'}")
      img(src="../../../../static/img/project-page/debug.svg")
</template>

<script>
  export default {
    name: 'projectSidebar'
    
  }
</script>

<style lang="scss" scoped>
  .wrapper {
    position: fixed;
    left: 0;
    padding-top: 20px;
    width: 40px;
    height: 100vh;
    background: #2E3340;
    box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);
  }
  .logo-link {
    display: block;
    padding-top: 10px;
    margin-left: 1px;
    margin-bottom: 5px;
  }
  .nav-link {
    position: relative;
    display: flex;
    height: 40px;
    justify-content: center;
    align-self: center;
    &.is-active {
      &:after {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        background-color: #fff;
        width: 2px;
        height: 100%;
      }
    }
  }
</style>
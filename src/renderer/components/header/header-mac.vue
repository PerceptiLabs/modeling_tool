<template lang="pug">
  .app-header
    //-ul.app-header_actions
      button.btn.btn--app-close(type="button" @click="appClose()").i.icon.icon-app-close-mac
      button.btn.btn--app-full(type="button" @click="appMinimize()").i.icon.icon-minus
      button.btn.btn--app-minify(type="button" @click="appMaximize()").i.icon.icon-app-fullscreen-mac
    .app-header_title PerceptiLabs
    the-menu(:show-menu="false")
</template>

<script>
  import TheMenu from '@/components/the-menu.vue'
export default {
  name: "HeaderMac",
  components: {TheMenu},
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  //$yellowBG: #f6c251;
  //$redBG: #ff6157;
  //$greenBG: #2acb42;

  .app-header {
    display: flex;
    align-items: center;
    height: $h-header-mac;
    background: linear-gradient(180deg, #4a4a4a 0%, #3e3e3e 100%);
  }
  /*<!--.app-header_actions {-->*/
  /*<!--  display: flex;-->*/
  /*<!--  margin-left: auto;-->*/
  /*<!--  -webkit-app-region: no-drag;-->*/
  /*<!--  height: 100%;-->*/
  /*<!--  align-items: center;-->*/

  /*<!--  .btn {-->*/
  /*<!--    display: flex;-->*/
  /*<!--    align-items: center;-->*/
  /*<!--    justify-content: center;-->*/
  /*<!--    width: 13px;-->*/
  /*<!--    height: 13px;-->*/
  /*<!--    margin-left: 7px;-->*/
  /*<!--    border-radius: 50%;-->*/
  /*<!--    font-size: 7px;-->*/
  /*<!--    font-weight: 900;-->*/
  /*<!--  }-->*/
  /*<!--  .btn&#45;&#45;app-minify {-->*/
  /*<!--    background: $greenBG;-->*/
  /*<!--    color: $greenBG;-->*/
  /*<!--    font-size: 9px;-->*/
  /*<!--    border: 1px solid #24ad38;-->*/
  /*<!--  }-->*/
  /*<!--  .btn&#45;&#45;app-full {-->*/
  /*<!--    background: $yellowBG;-->*/
  /*<!--    color: $yellowBG;-->*/
  /*<!--    border: 1px solid #d1a545;-->*/
  /*<!--  }-->*/
  /*<!--  .btn&#45;&#45;app-close {-->*/
  /*<!--    background: $redBG;-->*/
  /*<!--    color: $redBG;-->*/
  /*<!--    border: 1px solid #d9524a;-->*/
  /*<!--  }-->*/
  /*<!--}-->*/
  /*<!--.app-header_actions:hover {-->*/
  /*<!--  .btn&#45;&#45;app-close {-->*/
  /*<!--    color: #662723;-->*/
  /*<!--  }-->*/
  /*<!--  .btn&#45;&#45;app-full {-->*/
  /*<!--    color: #624e20;-->*/
  /*<!--  }-->*/
  /*<!--  .btn&#45;&#45;app-minify {-->*/
  /*<!--     color: #11511a;-->*/
  /*<!--  }-->*/
  /*<!--}-->*/

  .app-header_title {
    font-size: 12px;
    flex-grow: 1;
    text-align: center;
  }
</style>

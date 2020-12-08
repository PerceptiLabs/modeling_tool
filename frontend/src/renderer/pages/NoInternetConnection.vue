<template lang="pug">
  div.no-internet-connection-wrapper
    h1.page-title Can't connect to login server
</template>

<script>
export default {
  name: "NoInternetConnection",
  created() {
    window.addEventListener('online', function(event){
      window.location.reload();
    });
  }
}
</script>
<style lang="scss" scoped>
.no-internet-connection-wrapper {
  display: flex;
  justify-content: center;
}
.page-title {
  font-weight: bold;
  margin-top: 35vh;
}
</style>
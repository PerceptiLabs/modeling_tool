<template lang="pug">
  .test.form_row
    input(type="text" v-model="path")
    button.btn.btn--dark-blue-rev(type="button" @click="sendTest") Send
</template>

<script>
  import {coreRequest}  from "@/core/apiWeb.js";
export default {
  name: "test",
  data() {
    return {
      path: ''
    }
  },
  methods: {
    coreRequest,
    sendTest() {
      const theData = {
        action: 'checkCore',
        value: ''
      };
      this.coreRequest(theData, this.path)
        .then((data)=> {
          this.$store.commit('mod_api/SET_statusLocalCore', 'online')
        })
        .catch((err) =>{
          console.log(err);
        });
      // var wsUri = "wss://echo.websocket.org/";
      // let websocket = new WebSocket(wsUri);
      // websocket.onopen = function(evt) { onOpen(evt) };
      // websocket.onclose = function(evt) { onClose(evt) };
      // websocket.onmessage = function(evt) { onMessage(evt) };
      // websocket.onerror = function(evt) { onError(evt) };
      //
      //
      // function onOpen(evt)
      // {
      //   console.log("CONNECTED");
      //   doSend("WebSocket rocks");
      // }
      //
      // function onClose(evt)
      // {
      //   console.log("DISCONNECTED");
      // }
      //
      // function onMessage(evt)
      // {
      //   //console.log('<span style="color: blue;">RESPONSE: ' + evt.data+'</span>');
      //   console.log('RESPONSE ', evt);
      //   websocket.close();
      // }
      //
      // function onError(evt)
      // {
      //   console.log('ERROR ', evt);
      // }
      //
      // function doSend(message)
      // {
      //   console.log("SENT: " + message);
      //   websocket.send(message);
      // }
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";

</style>

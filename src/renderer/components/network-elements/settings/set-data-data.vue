<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
      )
        h3 {{ tab }}
    .popup_body()
    .popup_body()


</template>

<script>
  export default {
    name: 'SetDataData',
    components: {

    },
    data() {
      return {

        tabs: ['Computer', 'Cloud']
      }
    }
  }
</script>

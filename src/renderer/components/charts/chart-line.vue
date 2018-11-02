<template lang="pug">
  v-chart.base-chart(
    :auto-resize="true"
    theme="quantum"
    :options="chartData"
  )
</template>

<script>

export default {
  name: "ChartLine",
  props: ['chartData'],
  data() {
    return {

    }
  },
  methods: {

  }
}
</script>

<style lang="scss" scoped>

</style>

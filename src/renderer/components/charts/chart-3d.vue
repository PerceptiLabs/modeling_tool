<template lang="pug">
  v-chart(
    :auto-resize="true"
    theme="quantum"
    :options="chartData"
  )
</template>

<script>
export default {
  name: "ChartD3",
  props: {
    chartLabel: {
      type: String,
      default: ''
    },
    chartData: {
      type: Object,
      default: function() {
        return {}
      }
    },
  },
  data() {
    return {
      fullView: false
    }
  },
  methods: {
    toggleFullView() {
      this.fullView = !this.fullView
    }
  }
}
</script>

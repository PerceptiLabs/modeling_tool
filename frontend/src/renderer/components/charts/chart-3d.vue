<template lang="pug">
  v-chart(
    :auto-resize="true"
    :theme="currentTheme"
    :options="chartData"
  )
</template>

<script>
import { mapState } from 'vuex';
  import { THEME_DARK, THEME_LIGHT } from '@/core/constants.js';
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
    invert: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    ...mapState({
      theme:                      state => state.globalView.theme
    }),
    currentTheme () {
      if( this.invert ) {
        return this.theme === THEME_DARK ? THEME_LIGHT : THEME_DARK
      }
      return this.theme;
    }
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

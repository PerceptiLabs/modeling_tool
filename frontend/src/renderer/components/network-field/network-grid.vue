<template lang="pug">
  svg(v-if="isGridEnabled" :style="gridStyle" width="100%" height="100%" xmlns='http://www.w3.org/2000/svg')
    defs
      pattern#smallGrid(:width="smallGap" :height="smallGap" patternUnits='userSpaceOnUse')
        path(:d="`M ${smallGap} 0 L 0 0 0 ${smallGap}`" fill='none' stroke='gray' stroke-width='0.5')
      pattern#grid(width='150' height='150' patternUnits='userSpaceOnUse')
        rect(:width='bigGap' :height='bigGap' fill='url(#smallGrid)')
        path(:d='`M ${bigGap} 0 L 0 0 0 ${bigGap}`' fill='none' stroke='gray' stroke-width='1')
    rect(width='100%' height='100%' fill='url(#grid)')
</template>

<script>
  import { workspaceGridSmallGapSize, workspaceGridBigGapSize } from "@/core/constants.js"
  export default {
    name: "NetworkGrid",
    data: function() {
      return {
        smallGap: workspaceGridSmallGapSize,
        bigGap: workspaceGridBigGapSize
      }
    },
    props: {
      gridStyle: {
        type: Object,
        default: {},
      }
    },
    computed: {
      isGridEnabled() {
        return this.$store.state.globalView.isGridEnabled;
      },
    }
  }
</script>
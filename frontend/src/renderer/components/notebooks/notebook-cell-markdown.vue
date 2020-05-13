<template>
  <div class="cell-contents">
    <div class="markdown" v-html="sourceInMarkdown"></div>
  </div>
</template>


<script>
import Showdown from 'showdown';

export default {
  props: {
    cell: {
      default: ''
    }
  },
  data() {
    return {
      showdownConverter: null
    };
  },
  computed: {
    sourceInMarkdown() {
      if (!this.cell.source) { return ''; }
      if (!this.showdownConverter) { return ''; }

      return this.showdownConverter.makeHtml(this.cell.source);
    }
  },
  created() {
    this.showdownConverter = new Showdown.Converter();
  }
}
</script>

<style lang="scss" scoped>

.cell-contents {
    padding-left: 0.5rem;
    text-align: left;
}

.markdown {
    font-family:'Courier New', Courier, monospace;
}
</style>
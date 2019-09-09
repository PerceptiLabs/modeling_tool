<template lang="pug">
  .accordion
    .accordion-item(
      v-for="(item, i) in accordionTitle"
      :key="item.i"
      :class="{'accordion-item--open': tabSelected === i}"
    )
      button.accordion-item_btn.btn.btn--link(type="button" @click="setTab($event, i)")
        i.icon.icon-shevron-right
        span(v-html="item.html")
      .accordion-item_content
        .accordion-item_content-wrap
          slot(:name="item.name")

</template>

<script>
export default {
  name: 'BaseAccordion',
  props: {
    accordionTitle: {
      type: Array,
      default: function() {
        return []
      }
    }
  },
  data() {
    return {
      tabSelected: -1,
    }
  },
  computed: {
    wrapStyle() {
      return {
        maxHeight: this.wrapHeight
      }
    }
  },
  methods: {
    setTab(ev, i) {
      let acc = ev.target.closest('.accordion');
      let arrItems = acc.querySelectorAll('.accordion-item_content');
      if(this.tabSelected === i) {
        this.tabSelected = -1;
        arrItems[i].style = `max-height: 0px`
      }
      else {
        let wrapHeight = acc.querySelectorAll('.accordion-item_content-wrap')[i].clientHeight;
        this.tabSelected = i;
        arrItems.forEach((el)=> {
          el.style = `max-height: 0px`;
        });
        arrItems[i].style = `max-height: ${wrapHeight}px;`;
        setTimeout(()=>{arrItems[i].style=`max-height: ${wrapHeight}px; overflow: visible;`}, 300)
      }
    },
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  $acc-left-indent: 2rem;
  $acc-top-indent: 1.5rem;

  .accordion-item {
    border-bottom: 1px solid $bg-toolbar;
  }
  .accordion-item_btn {
    display: block;
    width: 100%;
    text-align: left;
    padding: $acc-top-indent $acc-left-indent;
    font-size: 1.4rem;
    .icon {
      @include multi-transition(transform);
      display: inline-block;
    }
    span {
      margin-left: 1rem;
    }
  }
  .accordion-item_content {
    @include multi-transition(max-height);
    max-height: 0;
    overflow: hidden;
  }
  .accordion-item_content-wrap {
    padding: $acc-top-indent $acc-left-indent;
  }
  .accordion-item--open {
    .accordion-item_btn .icon {
      transform: rotate(90deg);
    }
  }
</style>

<template lang="pug">
  .accordion(:class="{'v-2': isNewUi}")
    .accordion-item(
      v-for="(item, i) in accordionTitle"
      :key="item.i"
      :class="{'accordion-item--open': tabSelected === i}"
    )
      button.accordion-item_btn.btn.btn--link(type="button" @click="setTab($event, i)")
        div(v-if="isNewUi").accordion-triangle
        i(v-else).icon.icon-shevron-right
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
    },
    isNewUi: {
      type: Boolean,
      default: function() {
        return false;
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
  $acc-left-indent: 2rem;
  $acc-top-indent: 1.5rem;
  .accordion {
    &.v-2 {
      .accordion-item {
        border-bottom: 1px solid #3F4C70;
      }
      .accordion-item_btn {
        position: relative;
        padding: 10px 0; 
        font-family: Nunito Sans;
        font-style: normal;
        font-weight: normal;
        font-size: 12px;
        line-height: 16px;
        color: #C4C4C4;
      }
      .accordion-item_content-wrap {
        padding: 0 10px;
      }
      .accordion-item--open {
        .accordion-item_btn .accordion-triangle {
          transform: rotate(90deg);
        }
      }
    }
  }
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
  .accordion-triangle {
    position: absolute;
    left: 0;
    top: 15px;
    border-left: 3px solid #E1E1E1;
    border-bottom: 3px solid transparent;
    border-top: 3px solid transparent;
  }
</style>

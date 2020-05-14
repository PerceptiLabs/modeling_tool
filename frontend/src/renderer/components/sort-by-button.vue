<template lang="pug">
  div.button
    | Sort by
    ul.list
      li.head(@click="$emit('onSelectHandler', 0)")
        span None
        img.is-selected(v-if="optionSelected === 0" src="../../../static/img/drop-down-active.svg")
      li(v-for="option in options" :key="option.name" @click="$emit('onSelectHandler', option.value)")
        img.is-selected(v-if="optionSelected === option.value" src="../../../static/img/drop-down-active.svg")
        span {{option.name}}
</template>

<script>
  export default {
    name: 'sortByButton',
    props: {
      options: {
        type: Array,
        default: [],
      },
      optionSelected: {
        type: Number,
        default: 0,
      }
    }
  }

</script>

<style lang="scss" scoped>
  .button {
    position: relative;
    font-size: 16px;
    font-weight: bold;
    display: flex;
    cursor: pointer;
    background: transparent;
    border-radius: 5px;
    padding: 3px 29px 3px 9px;
    margin: 0 10px;
    color: #E1E1E1;
    line-height: 23px;
    &:hover {
      background: #383F50;
      .list {
        display: block;
      }
    }
    &:after {
      content: "";
      position: absolute;
      right: 5px;
      top: 50%;
      transform: translateY(-50%);
      border-left: 4px solid transparent;
      border-right: 4px solid transparent;
      border-top: 6px solid #fff;
    }
  }
  .list {
    display: none;
    position: absolute;
    z-index: 10;
    top: 28px;
    right: 0;
    min-width: 200px;
    list-style: none;
    background: #23252A;
    border: 1px solid #363E51;
    box-sizing: border-box;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
    border-radius: 5px;
    font-weight: 400;
    padding-bottom: 10px !important;
    li {
      position: relative;
      padding-left: 35px;
      line-height: 26px;
      &:hover {
        background: rgba(97, 133, 238, 0.75);
      }
    }
  }
  .head {
    border-bottom: 1px solid #363E51;
    line-height: 44px !important;
    margin-bottom: 10px;
  }
  .is-selected {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
  }
</style>
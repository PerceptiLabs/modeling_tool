<template lang="pug">
  .custom-select.js-clickout
    button.custom-select_view.input(type="button"
      :class="{'open-list': isOpenList, 'text-placeholder': !value.length}"
      @click="openList"
      )
      span {{ labelText }}
      i.icon.icon-shevron

    ul.custom-select_option-list.action-list(v-show="isOpenList")
      template(v-if="selectMultiple")
        li.custom-select_option
          button.action-list_btn(type="button"
            @click="selectAllBtn.action"
            )
            span.action-list_icon.icon(:class="selectAllBtn.iconClass")
            span.action-list_btn-text Select All
        li.custom-select_separator

      li.custom-select_option(
        v-for="(option, i) in selectOptions"
        :key="i"
        )

        span.action-list_sublist-area(v-if="option.sublist")
          span.sublist-area_text(@click.stop="openSubList") {{ option.text }}
          label.sublist-area-box
            ul.sublist-area_list(v-show="isOpenSubList")
              li.sublist_select(v-for="(sublistOption, i) in option.sublist")
                label.action-list_btn
                  input.action-list_input(
                    :type="typeSelectList"
                    :name="uniqName"
                    :value="sublistOption.value"
                    v-model="checkedOptions"
                  )
                  span.action-list_icon.icon.icon-check-mark(v-if="selectMultiple")
                  .action-list_bg
                  span.action-list_btn-text {{ sublistOption.text }}

        label.action-list_btn(v-else)
          input.action-list_input(
            :type="typeSelectList"
            :name="uniqName"
            :value="option.value"
            v-model="checkedOptions"
          )
          span.action-list_icon.icon.icon-check-mark(v-if="selectMultiple")
          .action-list_bg
          span.action-list_btn-text {{ option.text }}



</template>

<script>
  import clickOutside     from '@/core/mixins/click-outside.js'
export default {
  name: "BaseSelect",
  mixins: [clickOutside],
  props: {
    value: {
      type: [String, Array],
      default: ''
    },
    selectOptions: {
      type: Array,
      default: function () {
        return []
      }
    },
    selectMultiple: {
      type: Boolean,
      default: false
    },
    selectPlaceholder: {
      type: String,
      default: ''
    },
  },
  created() {
    this.defaultModel();
  },
  mounted() {
    if(this.value.length) this.checkedOptions = this.value
  },
  data() {
    return {
      checkedOptions: null,
      isOpenList: false,
      isOpenSubList: false
    }
  },
  computed: {
    typeSelectList() {
      return this.selectMultiple ? 'checkbox' : 'radio'
    },
    uniqName() {
      return this._uid + 'selectid'
    },
    labelText() {
      if(this.value.length) {
        let checkedTextList = [];
        this.selectOptions.forEach((item)=> {
          if(item.sublist) {
            item.sublist.forEach((subItem) => {
              if(this.checkedOptions.includes(subItem.value)) checkedTextList.push(subItem.text)
            })
          }
          if(this.checkedOptions.includes(item.value)) checkedTextList.push(item.text)
        });
        return checkedTextList.join(', ')
      }
      else return this.selectPlaceholder;
    },
    selectAllBtn() {
      let all = this.selectOptions.length || 0;
      let check = this.checkedOptions.length;
      console.log(this.selectOptions, this.checkedOptions);
      if(all === check)             return {iconClass: 'icon-appMinimaze',  action: ()=> this.defaultModel()};
      if(all > check && check > 0)  return {iconClass: 'icon-appClose',     action: ()=> this.defaultModel()};
      if(check === 0)               return {iconClass: 'icon-check-mark',   action: ()=> this.enableAll()};
      return {iconClass: 'icon-check-mark',   action: ()=> this.defaultModel()};
    }
  },
  watch: {
    checkedOptions(val) {
      this.$emit('input', val);
      if(!this.selectMultiple) this.closeList()
    },
  },
  methods: {
    defaultModel() {
      this.selectMultiple ? this.checkedOptions = [] : this.checkedOptions = ''
    },
    enableAll() {
      this.selectOptions.forEach((item)=> this.checkedOptions.push(item.value));
    },
    openList() {
      this.isOpenList ? this.closeList() : this.isOpenList = true
    },
    closeList() {
      this.isOpenList = false;
    },
    clickOutsideAction() {
      this.closeList()
    },
    openSubList() {
      this.isOpenSubList = !this.isOpenSubList;
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .custom-select {
    width: 100%;
    position: relative;
    min-width: 100px;
  }
  .custom-select_view {
    display: flex;
    align-items: center;
    cursor: default;
    text-align: left;
    span {
      flex: 1 1 100%;
      line-height: 1.25;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
    .icon {
      flex: 0 0 auto;
      transform: rotate(90deg);
    }
    &.open-list {
      .icon {
        transform: rotate(-90deg);
      }
    }
    &.text-placeholder {
      font-style: italic;
      font-weight: 300;
    }
  }
  .custom-select_option-list {
    position: absolute;
    z-index: 2;
    top: 100%;
    left: 0;
    max-height: 13.5rem;
    overflow: auto;
  }
  .custom-select_separator {
    border-top: 1px solid;
  }
  .custom-select_option {
    cursor: default;
    &:first-child {
      border-radius: $bdrs $bdrs 0 0;
    }
    &:last-child {
      border-radius: 0 0 $bdrs $bdrs;
    }
  }
  .action-list_btn {
    position: relative;
    justify-content: flex-start;
  }
  .action-list_input {
    position: absolute;
    left: -9999px;
    opacity: 0;
    &:not(:checked) + .action-list_icon {
      opacity: 0;
    }
    &:checked ~ .action-list_bg {
      position: absolute;
      z-index: -1;
      background-color: #6E778C;
      left: 0;
      right: 0;
      top: 0;
      bottom: 0;
    }
  }
  .action-list_icon {
    margin-right: 1rem;
  }
</style>

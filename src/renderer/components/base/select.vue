<template lang="pug">
  .custom-select
    button.custom-select_view.input(type="button"
      :class="{'open-list': isOpenList, 'text-placeholder': !value.length}"
      @click="openList"
      )
      span {{ labelText }}
      i.icon.icon-shevron.icon--open

    ul.custom-select_option-list.action-list(v-show="isOpenList")
      template(v-if="selectMultiple")
        li.custom-select_option
          button.action-list_btn(type="button" @click="selectAllBtn.action")
            span.action-list_icon.icon(:class="selectAllBtn.iconClass")
            span.action-list_btn-text Select All
        li.custom-select_separator

      li.custom-select_option(
        v-for="(option, i) in selectOptions"
        :key="i"
        :class="{'custom-select_option-open': openIndexSublist === i}"
        )
        template(v-if="option.sublist")
          button.action-list_btn(type="button" @click="openSubList(i)" )
            span.action-list_icon.icon.icon-check-mark(v-if="selectMultiple")
            .action-list_bg
            span.action-list_btn-text {{ option.text }}
            i.icon.icon-shevron.icon--open
          ul.action-list.action-list--sub-list
            li.custom-select_option(
              v-for="(subOption, index) in option.sublist"
              :key="index"
            )
              label.action-list_btn
                input.action-list_input(
                  :type="typeSelectList"
                  :name="uniqName"
                  :value="subOption.value"
                  v-model="checkedOptions"
                )
                span.action-list_icon.icon.icon-check-mark(v-if="selectMultiple")
                .action-list_bg
                span.action-list_btn-text {{ subOption.text }}
        template(v-else)
          label.action-list_btn
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
export default {
  name: "BaseSelect",
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
  beforeDestroy() {
    this.checkedOptions = null;
    this.openIndexSublist = null
  },
  data() {
    return {
      isReady: false,
      checkedOptions: null,
      isOpenList: false,
      openIndexSublist: null
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
        addSelectedText(this.value, this.selectOptions, checkedTextList);
        return checkedTextList.join(', ')
      }
      else return this.selectPlaceholder;

      function addSelectedText(selectVal, arr, out) {
        arr.forEach((item)=> {
          if(selectVal.includes(item.value)) out.push(item.text);
          if(item.sublist) addSelectedText(selectVal, item.sublist, out);
        })
      }
    },
    selectAllBtn() {
      let all = this.selectOptions.length || 0;
      let check = this.checkedOptions.length;
      if(all === check)             return {iconClass: 'icon-app-minimize',  action: ()=> this.defaultModel()};
      if(all > check && check > 0)  return {iconClass: 'icon-app-close',     action: ()=> this.defaultModel()};
      if(check === 0)               return {iconClass: 'icon-check-mark',   action: ()=> this.enableAll()};
      return {iconClass: 'icon-check-mark',   action: ()=> this.defaultModel()};
    }
  },
  watch: {
    checkedOptions(newVal, oldVal) {
      if(oldVal === null) return;
      if(!this.selectMultiple) this.closeList();
      this.$emit('input', newVal);
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
    openSubList(index) {
      this.openIndexSublist === index
        ? this.openIndexSublist = null
        : this.openIndexSublist = index
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
    .icon--open {
      flex: 0 0 auto;
    }
    &.open-list {
      .icon--open {
        transform: rotate(-180deg);
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
    .icon--open {
      margin-left: auto;
    }
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
  .action-list--sub-list {
    display: none;
    box-shadow: none;
    padding-left: 2.5rem;

  }
  .custom-select_option-open {
    .action-list--sub-list {
      display: block;
    }
    .action-list_btn {
      .icon--open {
        transform: rotate(-180deg);
      }
    }
  }
</style>

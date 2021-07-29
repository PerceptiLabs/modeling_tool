<template lang="pug">
  .custom-select(:class="styleType")
    button.custom-select_view.input(type="button"
      :class="{'open-list': isOpenList, 'text-placeholder': !value.length}"
      :disabled="disabled"
      @click="openList"
      v-click-outside="closeList"
      )
      span.thin-font {{ labelText }}
      i.icon.icon-shevron.icon--open(v-if="!disabled")

    perfect-scrollbar(tag="ul").custom-select_option-list.action-list(
      :class="{'open': isOpenList}"
      v-show="isOpenList"
      )
      template(v-if="selectMultiple")
        li.custom-select_option
          base-checkbox.select_checkbox(v-if="showCheckbox && selectMultiple" @input="selectAllBtn.action" :value="selectAllBtn.selectStatus") SelectAll
          button.action-list_btn(v-else type="button" @click="selectAllBtn.action")
            span.action-list_icon.icon(:class="selectAllBtn.iconClass")
            span.action-list_btn-text Select All
        li.custom-select_separator

      li.custom-select_option(
        v-for="(option, i) in trueModel"
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
              label.action-list_btn.thin-font
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
          base-checkbox.select_checkbox(
            v-if="showCheckbox && selectMultiple" 
            :value="checkedOptions.includes(option.value)"
            @input="toggleItem(option)"
          ) {{option.text}}
          label.action-list_btn(v-else @click.stop="clickList")
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
    showCheckbox: {
      type: Boolean,
      default: false,
    },
    styleType: { type: String, default: '' },
    disabled: {
      type: Boolean,
      default: false,
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
    trueModel() {
      const optionsList = this.selectOptions;
      if(!optionsList.length) return optionsList;
      if( optionsList[0].constructor.name === 'Object') return optionsList;
      else return optionsList.map((el)=> { return { text: el, value: el, }})
    },
    labelText() {
      if(this.value.length) {
        let checkedTextList = [];
        addSelectedText(this.value, this.trueModel, checkedTextList);
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
      let all = this.trueModel.length || 0;
      let check = this.checkedOptions.length;

      if(all === check)             return {iconClass: 'icon-app-minimize', selectStatus: true,  action: ()=> this.defaultModel()};
      if(all > check && check > 0)  return {iconClass: 'icon-app-close',    selectStatus: true, action: ()=> this.defaultModel()};
      if(check === 0)               return {iconClass: 'icon-check-mark',   selectStatus: false, action: ()=> this.enableAll()};
      return {iconClass: 'icon-check-mark',  selectStatus: false, action: ()=> this.defaultModel()};
    }
  },
  watch: {
    checkedOptions(newVal, oldVal) {
      if(oldVal === null) return;
      this.$emit('input', newVal);
    },
    isOpenList(newVal, oldVal) {
      if(oldVal === null) return;
      this.$emit('isOpen', newVal);
    }
  },
  methods: {
    clickList() {
      if(!this.selectMultiple) this.closeList();
    },
    defaultModel() {
      this.selectMultiple ? this.checkedOptions = [] : this.checkedOptions = ''
    },
    enableAll() {
      this.trueModel.forEach((item)=> this.checkedOptions.push(item.value));
    },
    openList() {
      this.isOpenList ? this.closeList() : this.isOpenList = true
    },
    closeList() {
      this.isOpenList = false;
    },
    toggleItem(option) {
      if (!this.selectMultiple) {
        return;
      }
      if (this.checkedOptions && this.checkedOptions.includes(option.value)) {
        this.checkedOptions = this.checkedOptions.filter((v) => v !== option.value);
      } else {
        if (this.checkedOptions) {
          this.checkedOptions = [...this.checkedOptions, option.value];
        } else {
          this.checkedOptions = [option.value];
        }
      }
      this.openList();
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

  .thin-font {
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 300;
    font-size: 12px;
    line-height: 1.6rem;
  }

  .custom-select {
    width: 100%;
    position: relative;
    min-width: 100px;
    transition: 3s;
    &::after {
      transition: 0.15s;
      content: '';
      position: absolute;
      width: calc(100% + 10px);
      height: calc(100% + 10px);
      top: -5px;
      left: -5px;
      background-color: transparent;
      pointer-events: none;
      border: 0px solid rgba(#B6C7FB, .5);
      border-radius: 2px;
      z-index: 2;
    }
    &.active {
      &::after {
        border: 5px solid rgba(#B6C7FB, .5);
      }
      // .custom-select_view {
      //   outline: 3px solid rgba(#B6C7FB, .7);  
      //   // border-radius: 2px 1px 1px 1px;

      // }
    }
  }
  .custom-select_view {
    display: flex;
    align-items: center;
    cursor: default;
    text-align: left;
    background: #363E51;
    height: 3.5rem; 
    border: 1px solid #363E51;
    
    .darken & {
      background-color: #202532;
      border: 1px solid #5E6F9F;
    }

    .text-center & {
      text-align: center;
    }

    .sidebar-setting-content & {
      // background: transparent;
      // height: 17px;
      // border: none;
      // color: #C4C4C4;
    }

    .network-component-footer-wrapper & {
      height: 17px;
      width: 55px;
      margin-left: 40px;
      background: #131B30;
      border: 1px solid rgba(97, 133, 238, 0.4);
      border-radius: 1px;
      font-size: 10px;
    }


    span {
      flex: 1 1 100%;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
    .icon--open {
      flex: 0 0 auto;
      transform-origin: 50% 50%;
      .text-center & {
        position: absolute;
        right: 10px;
      }
    }

    &:focus {
      border: 1px solid rgb(149, 152, 161);
    }

    &.open-list {
      border: 1px solid #B6C7FB;

      .icon--open {
        transform: rotate(-180deg);
      }
    }
    &.text-placeholder {
      font-style: italic;
      font-weight: 300;
      color: #C4C4C4;
    }

    &:disabled {
      background: #171B25;
    }
  }
  .custom-select_option-list {
    position: absolute;
    z-index: 3;
    top: 100%;
    left: 0;
    max-height: 13.5rem;
    overflow: auto;
    background-color: #3F4C70;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
    border-style: solid;
    border-color: #B6C7FB;
    border-width: 0 1px 1px 1px;
  }
  .custom-select_separator {
    border-top: 1px solid;
  }
  .custom-select_option {    
    cursor: default;  

    label {
      height: 3rem;
    }

    &:first {
      border-radius: 0;
    }
    &:last-of-type {
      border-radius: 0 0 $bdrs $bdrs;
    }

    .select_checkbox {
      width: 100%;
      padding: 0 20px;
    }
  }

  .action-list_btn {
    position: relative;
    justify-content: flex-start;
    .icon--open {
      margin-left: auto;
    }
    .text-center & {
      justify-content: center;
    }
    
    text-align: center;

  }
  .action-list_btn-text {
    .text-center & {
      margin-right: 0;
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
      background: rgba(97, 133, 238, 0.5);
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

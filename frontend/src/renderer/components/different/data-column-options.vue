<template lang="pug">
  header(
    v-if="showIfTypeIs(['image', 'numerical'])"
    :class="{'is-open': isOpen}"
    v-click-outside="closeDropDown"
  )
    div.svg-wrapper(@click="toggle()")
      svg(width="12" height="9" viewBox="0 0 12 9" fill="none" xmlns="http://www.w3.org/2000/svg")
        path(fill-rule="evenodd" clip-rule="evenodd" d="M0.5 8.5C0.5 8.36739 0.552679 8.24021 0.646447 8.14645C0.740215 8.05268 0.867392 8 1 8H5C5.13261 8 5.25979 8.05268 5.35355 8.14645C5.44732 8.24021 5.5 8.36739 5.5 8.5C5.5 8.63261 5.44732 8.75979 5.35355 8.85355C5.25979 8.94732 5.13261 9 5 9H1C0.867392 9 0.740215 8.94732 0.646447 8.85355C0.552679 8.75979 0.5 8.63261 0.5 8.5ZM0.5 4.5C0.5 4.36739 0.552679 4.24021 0.646447 4.14645C0.740215 4.05268 0.867392 4 1 4H8C8.13261 4 8.25979 4.05268 8.35355 4.14645C8.44732 4.24021 8.5 4.36739 8.5 4.5C8.5 4.63261 8.44732 4.75979 8.35355 4.85355C8.25979 4.94732 8.13261 5 8 5H1C0.867392 5 0.740215 4.94732 0.646447 4.85355C0.552679 4.75979 0.5 4.63261 0.5 4.5ZM0.5 0.5C0.5 0.367392 0.552679 0.240215 0.646447 0.146447C0.740215 0.0526785 0.867392 0 1 0H11C11.1326 0 11.2598 0.0526785 11.3536 0.146447C11.4473 0.240215 11.5 0.367392 11.5 0.5C11.5 0.632608 11.4473 0.759785 11.3536 0.853553C11.2598 0.947321 11.1326 1 11 1H1C0.867392 1 0.740215 0.947321 0.646447 0.853553C0.552679 0.759785 0.5 0.632608 0.5 0.5Z" fill="white")
    main
      div.main-content
        base-checkbox(
          v-if="showIfTypeIs(['image', 'numerical'])"
          v-model="options.normalize.value" :isNewUi="true") Normalize
        div(
          v-if="options.normalize.value"
          class="image-random-option-select d-flex flex-column")
          base-radio(group-name="normalizeTypeGroup" value-input="standardization" v-model="options.normalize.type")
            span Standardization
          base-radio(group-name="normalizeTypeGroup" value-input="min-max" v-model="options.normalize.type")
            span Min Max
        template(v-if="showIfTypeIs(['image'])")
          base-checkbox(
            v-model="options.random_flip.value" :isNewUi="true") Random Flip
          div(
            v-if="options.random_flip.value"
            class="image-random-option-select d-flex flex-column")
            base-radio(group-name="randomFlipTypeGroup" value-input="vertical" v-model="options.random_flip.mode")
              span Vertical
            base-radio(group-name="randomFlipTypeGroup" value-input="horizontal" v-model="options.random_flip.mode")
              span Horizontal
            base-radio(group-name="randomFlipTypeGroup" value-input="both" v-model="options.random_flip.mode")
              span Both
            .d-flex.flex-column
              label.form_label.text-left Seed:
              input.form_input(type="text" v-model="options.random_flip.seed")
        footer.d-flex.justify-content-end
          button.btn.btn--primary(
            @click="onSave"
          ) Save
  div(v-else) &nbsp;   
</template>
<script>

export default {
  name: "DataColumnOptions",
  props:{
    index: {
      type: Number,
      default: null,
    },
    columnSelectedType: {
      type: Array,
      default: [],
    }
  },
  data() {
    return {
      isOpen: false,
      options: {
        normalize: { value: false, type: 'standardization' },
        random_flip: { value: false, mode: 'both', seed: 123 }
      }
    }
  },
  computed: {
    dataTypeSelected() {
      return this.columnSelectedType[this.index];
    }
  },
  methods: {
    onSave(){
      const saveResponse = {};
      if(this.dataTypeSelected === 'image' && this.options.random_flip.value) {
        saveResponse['random_flip'] = this.options.random_flip;
      }
      if(this.showIfTypeIs(['image', 'numerical']) && this.options.normalize.value) {
        saveResponse['normalize'] = { type: this.options.normalize.type };
      }

      this.$emit('handleChange', this.index, saveResponse);
      this.isOpen = false;
    },
    toggle(){
      this.isOpen = !this.isOpen;
    },
    closeDropDown(){
      this.isOpen = false;
    },
    showIfTypeIs(arrOfAllowedTypes = []) {
      return arrOfAllowedTypes.some(el => el === this.dataTypeSelected);
    }
  }
}
</script>
<style lang="scss" scoped>
header {
  position: relative;
  &.is-open {
    main {
      display: block;
    }
    .svg-wrapper {
      background-color: #7B7B7B;
    }
  }
}
main {
  display: none;
  position: absolute;
  background-color: #242B3A;
  right: -7px;
  top: 35px;
  z-index: 1;
}
.svg-wrapper {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 25px;
  height: 25px;
  padding: 2px 5px;
  border-radius: 50%;
  transition: 0.3s;
  &:hover {
    background-color: #7B7B7B;
  }
}
.main-content {
  position: relative;
  border: 1px solid rgba(97, 133, 238, 0.4);
  padding: 10px;
  display: flex;
  flex-direction: column;
  &::after {
    content: '';
    position: absolute;
    top: -7px;
    right: 12px;
    width: 12px;
    height: 12px;
    background-color: #242B3A;
    border-left: 1px solid rgba(97, 133, 238, 0.4);
    border-top: 1px solid  rgba(97, 133, 238, 0.4);
    transform: rotate(45deg)
  }
}

footer {
  margin-top: 20px;
  .btn {
    min-width: auto;
    width: 51px;
    height: 25px;
  }
}
.custom-radio {
  padding: 0 !important;
}
.image-random-option-select {
  padding-left: 20px;
}
.text-left {
  text-align: left;
}
</style>

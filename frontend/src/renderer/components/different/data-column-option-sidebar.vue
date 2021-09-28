<template lang="pug">
  header(
    :class="{'is-open': isOpen}"
  )
    div.overlay(@click="onCancel")
    main
      .header
        .pre-processing-text.bold Pre-processing for {{columnNames[index]}}
        .popup-close(@click="onCancel")
          svg(width="8" height="8" viewBox="0 0 8 8" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M0.165255 0.165255C0.217507 0.112872 0.279579 0.0713107 0.347917 0.0429534C0.416256 0.0145962 0.489517 0 0.563505 0C0.637493 0 0.710755 0.0145962 0.779093 0.0429534C0.847431 0.0713107 0.909504 0.112872 0.961755 0.165255L3.93851 3.14313L6.91526 0.165255C6.96755 0.112956 7.02964 0.0714704 7.09797 0.0431664C7.16631 0.0148624 7.23954 0.000294507 7.31351 0.000294507C7.38747 0.000294507 7.4607 0.0148624 7.52904 0.0431664C7.59737 0.0714704 7.65946 0.112956 7.71176 0.165255C7.76405 0.217554 7.80554 0.279642 7.83384 0.347974C7.86215 0.416306 7.87672 0.489543 7.87672 0.563505C7.87672 0.637467 7.86215 0.710705 7.83384 0.779037C7.80554 0.847369 7.76405 0.909456 7.71176 0.961755L4.73388 3.93851L7.71176 6.91526C7.76405 6.96755 7.80554 7.02964 7.83384 7.09797C7.86215 7.16631 7.87672 7.23954 7.87672 7.31351C7.87672 7.38747 7.86215 7.4607 7.83384 7.52904C7.80554 7.59737 7.76405 7.65946 7.71176 7.71176C7.65946 7.76405 7.59737 7.80554 7.52904 7.83384C7.4607 7.86215 7.38747 7.87672 7.31351 7.87672C7.23954 7.87672 7.16631 7.86215 7.09797 7.83384C7.02964 7.80554 6.96755 7.76405 6.91526 7.71176L3.93851 4.73388L0.961755 7.71176C0.909456 7.76405 0.847369 7.80554 0.779037 7.83384C0.710705 7.86215 0.637467 7.87672 0.563505 7.87672C0.489543 7.87672 0.416306 7.86215 0.347974 7.83384C0.279642 7.80554 0.217554 7.76405 0.165255 7.71176C0.112956 7.65946 0.0714704 7.59737 0.0431664 7.52904C0.0148624 7.4607 0.000294507 7.38747 0.000294507 7.31351C0.000294507 7.23954 0.0148624 7.16631 0.0431664 7.09797C0.0714704 7.02964 0.112956 6.96755 0.165255 6.91526L3.14313 3.93851L0.165255 0.961755C0.112872 0.909504 0.0713107 0.847431 0.0429534 0.779093C0.0145962 0.710755 0 0.637493 0 0.563505C0 0.489517 0.0145962 0.416256 0.0429534 0.347917C0.0713107 0.279579 0.112872 0.217507 0.165255 0.165255Z")

      perfect-scrollbar
        .main-content
          div.mb-20
            base-checkbox.bold.size-16(
              v-if="showIfTypeIs(['image', 'numerical'])"
              v-model="options.normalize.value"
              ) Normalize
            div.mt-10(
              v-if="options.normalize.value"
              class="image-random-option-select d-flex flex-column")
              base-radio.mb-5(:group-name="'normalizeTypeGroup' + elementIndex" value-input="standardization" v-model="options.normalize.type")
                span Standardization
              base-radio(:group-name="'normalizeTypeGroup' + elementIndex" value-input="min-max" v-model="options.normalize.type")
                span Min Max
          template(v-if="showIfTypeIs(['image', 'mask'])")
            div.mb-20
              base-checkbox.bold.size-16(
                v-model="options.random_flip.value") Random Flip
              div.mt-10.settings-layer_section(
                v-if="options.random_flip.value"
                class="image-random-option-select d-flex flex-column")
                base-radio.mb-5(:group-name="'randomFlipTypeGroup' + elementIndex" value-input="vertical" v-model="options.random_flip.mode")
                  span Vertical
                base-radio.mb-5(:group-name="'randomFlipTypeGroup' + elementIndex" value-input="horizontal" v-model="options.random_flip.mode")
                  span Horizontal
                base-radio.mb-5(:group-name="'randomFlipTypeGroup' + elementIndex" value-input="both" v-model="options.random_flip.mode")
                  span Both
                .form_row
                  label.form_label Seed:
                  input.form_input(type="text" v-model="options.random_flip.seed")
            div.mb-20
              base-checkbox.bold.size-16(
                v-model="options.resize.value") Resize
              div.pl-20.mt-10(v-if="options.resize.value")
                div.d-flex.flex-column
                  base-radio.mb-5(:group-name="'resizeType' + elementIndex" value-input="automatic" v-model="options.resize.mode")
                    span Automatic
                  div.pl-20.d-flex.flex-column(v-if="options.resize.mode === 'automatic'")
                    base-radio.mb-5(:group-name="'resizeAutomaticType' + elementIndex" value-input="mode" v-model="options.resize.type")
                      span Dataset mode
                    base-radio.mb-5(:group-name="'resizeAutomaticType' + elementIndex" value-input="mean" v-model="options.resize.type")
                      span Dataset mean
                    base-radio.mb-5(:group-name="'resizeAutomaticType' + elementIndex" value-input="max" v-model="options.resize.type")
                      span Dataset max
                    base-radio.mb-5(:group-name="'resizeAutomaticType' + elementIndex" value-input="min" v-model="options.resize.type")
                      span Dataset min
                  base-radio.mb-5(:group-name="'resizeType' + elementIndex" value-input="custom" v-model="options.resize.mode")
                    span Custom
                  div.settings-layer_section.pl-20.d-flex.flex-column(v-if="options.resize.mode === 'custom'")
                    .form_row
                      label.form_label Width:
                      input.form_input(type="number" min="1" v-model="options.resize.width")
                    .form_row
                      label.form_label Height:
                      input.form_input(type="number" min="1" v-model="options.resize.height")
            div.mb-20
              base-checkbox.bold.size-16(
                v-model="options.random_rotation.value"
              ) Random rotation
              div.settings-layer_section.mt-10(class="pl-20 d-flex flex-column" v-if="options.random_rotation.value")
                base-radio.mb-5(:group-name="'randomRotationTypeGroup' + elementIndex" value-input="reflect" v-model="options.random_rotation.fill_mode")
                  span Reflect
                base-radio.mb-5(:group-name="'randomRotationTypeGroup' + elementIndex" value-input="constant" v-model="options.random_rotation.fill_mode")
                  span Constant
                base-radio.mb-5(:group-name="'randomRotationTypeGroup' + elementIndex" value-input="wrap" v-model="options.random_rotation.fill_mode")
                  span Wrap
                base-radio.mb-5(:group-name="'randomRotationTypeGroup' + elementIndex" value-input="nearest" v-model="options.random_rotation.fill_mode")
                  span Nearest
                .form_row(v-if="options.random_rotation.fill_mode === 'constant'")
                  label.form_label Fill:
                  input.form_input(type="number" v-model="options.random_rotation.fill_value")
    
                .form_row
                  label.form_label Factor:
                  input.form_input(type="number" v-model="options.random_rotation.factor")
                .form_row
                  label.form_label Seed:
                  input.form_input(type="number" v-model="options.random_rotation.seed")
            div.mb-20
              base-checkbox.bold.size-16(
                v-model="options.random_crop.value"
              ) Random Crop
              div.settings-layer_section.mt-10.pl-25(
                v-if="options.random_crop.value"
              )
                .form_row
                  label.form_label Seed:
                  input.form_input.w-150(type="text" v-model="options.random_crop.seed")
                .form_row
                  label.form_label Width:
                  input.form_input.w-150.text-left(type="number" min="1" v-model="options.random_crop.width")
                .form_row
                  label.form_label Height:
                  input.form_input.w-150.text-left(type="number" min="1" v-model="options.random_crop.height")
      footer.d-flex.justify-content-between
        button.btn.btn--secondary(
          @click="onCancel"
        ) Cancel
        button.btn.btn--primary(
          @click="onSave"
        ) Save
</template>
<script>
import { mapGetters } from 'vuex';
export default {
  name: "DataColumnOptionsSidebar",
  props:{
    columnSelectedType: {
      type: Array,
      default: [],
    },
    columnNames: {
      type: Array,
      default: function (){ return []}
    },
    elementIndex: {
      type: Number,
      default: null,
    },
    preprocessingTypes: {
      type: Array,
      default: null,
    }
  },
  data() {
    return {
      options: {
        normalize: { value: false, type: 'standardization' },
        random_flip: { value: false, mode: 'both', seed: 123 },
        random_crop: { value: false, seed: 123, width: 32, height: 32 },
        random_rotation: { value: false, fill_mode: '', fill_value: 0, seed: 123, factor: 0}, // fill_value = reflect|constant - fill_value|wrap|nearest	  
        resize: { value: true, width: 32, height: 32, mode: 'automatic', type: 'mode' }
      }
    }
  },
  computed: {
    dataTypeSelected() {
      try {
        return this.columnSelectedType[this.elementIndex];  
      } catch (e) {
        return null;
      }
    },
    ...mapGetters({
      index: 'mod_dataWizardPreprocessing/getElementPreProcessingIndex',
    }),
    isOpen() {
      return this.index === this.elementIndex
    }
  },
  mounted() {
    if (!this.preprocessingTypes) {
      this.onSave();
    } else {
      Object.keys(this.preprocessingTypes[this.elementIndex]).forEach((optionKey) => {
        this.options[optionKey] = {
          ...this.options[optionKey],
          ...this.preprocessingTypes[this.elementIndex][optionKey],
          value: true
        };
      })
    }
  },
  watch: {
    'dataTypeSelected': {
      handler(typeSelected) {
        this.onTypeChange(typeSelected);
        this.onSave();
      },
    },
  },
  methods: {
    onTypeChange(type) {
      if(type === 'mask') {
        this.options.resize.width = 224;
        this.options.resize.height = 224;
        this.options.resize.mode = 'custom';
      }
      if(type === 'image') {
        this.options.resize.width = 32;
        this.options.resize.height = 32;
        this.options.resize.mode = 'automatic';
      }
    },
    onSave(){
      const saveResponse = {};
      if(this.showIfTypeIs(['image', 'mask'])) {
        if(this.options.random_flip.value) {
          saveResponse['random_flip'] = this.options.random_flip;
        }
        if(this.options.resize.value) {

          const isAutomaticType = this.options.resize.mode === 'automatic';
          const isCustomType = this.options.resize.mode === 'custom';

          if(isAutomaticType) {
            saveResponse['resize'] = {
              mode: this.options.resize.mode,
              type: this.options.resize.type
            }
          }

          if(isCustomType) {
            saveResponse['resize'] = {
              mode: this.options.resize.mode,
              width: parseInt(this.options.resize.width, 10),
              height: parseInt(this.options.resize.height, 10)
            }
          }

        }
        if(this.options.random_crop.value) {
          saveResponse['random_crop'] = {
            seed: parseInt(this.options.random_crop.seed, 10),
            width: parseInt(this.options.random_crop.width, 10),
            height: parseInt(this.options.random_crop.height, 10),
          }
        }

        // Random rotation
        if(this.options.random_rotation.value) {
          saveResponse['random_rotation'] = {
            fill_mode: this.options.random_rotation.fill_mode,
            seed: parseInt(this.options.random_rotation.seed, 10),
            factor: parseFloat(this.options.random_rotation.factor),
          }
          if(this.options.random_rotation.fill_mode === 'constant') {
            saveResponse['random_rotation']['fill_value'] = parseFloat(this.options.random_rotation.fill_value);
          }
        }
      }
      if(this.showIfTypeIs(['image', 'numerical']) && this.options.normalize.value) {
        saveResponse['normalize'] = { type: this.options.normalize.type };
      }
      if (this.showIfTypeIs(['mask'])) {
        saveResponse['mask'] = true;
      }
      this.$emit('handleChange', this.elementIndex, saveResponse);
      this.onCancel();
    },
    onCancel(){
      this.$store.dispatch('mod_dataWizardPreprocessing/TOGGLE_elementPreProcessing', null);
    },
    toggle(){
    },
    showIfTypeIs(arrOfAllowedTypes = []) {
      return arrOfAllowedTypes.some(el => el === this.dataTypeSelected);
    }
  }
}
</script>
<style lang="scss" scoped>

header {
  &.is-open {
    main {
      display: flex;
      flex-direction: column;
    }
    .overlay {
      display: block;
    }
  }
}
main {
  display: none;
  position: absolute;
  right: 0;
  top: 0;
  z-index: 10;
  // margin-top: 65px;
  // height: calc(100% - 65px);
  height: 100%;
  width: 350px;
  background: theme-var($neutral-8);
  border-radius: 0 15px 15px 0;
}
.main-content {
  padding: 30px 25px 25px;
}

footer {
  margin-top: auto;
  padding: 20px;
}
.custom-radio {
  padding: 0 !important;
}
.image-random-option-select {
  padding-left: 20px;
}
.form_label {
  font-size: 16px;
}

.settings-layer_section {
  // padding: $popup-indent-top/2 $popup-indent-left;

	> .form_row {
		.form_label {
			flex: 0 0 30%;
			max-width: 30%;
		}
    
    .form_input {
      max-width: 70%;
    }
  }
}
// .form_input {
//   background: #222736;
//   border-radius: 2px;
//   border: 1px solid #5E6F9F;
//   height: 36px;
//   font-family: Roboto, 'sans-serif';
//   font-size: 14px;
//   line-height: 16px;
//   letter-spacing: 0.02em;
//   color: #E1E1E1;
//   padding-left: 10px;
//   transition: 0.3s;
//   &:focus {
//     border: 1px solid #B6C7FB;
//   }
// }
.header {
  padding: 25px;
  background: theme-var($neutral-7);
  border: $border-1; 
  border-radius: 0 15px 0 0;
}
.pre-processing-text {
  font-family: Roboto, 'sans-serif';
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
}
.pl-20 {
  padding-left: 20px;
}
.text-left {
  text-align: left;
}
.pl-25 {
  padding-left: 25px;
}
.mt-10 {
  margin-top: 10px;
}
.mb-5 {
  margin-bottom: 5px;
}
.mb-10 {
  margin-bottom: 10px;
}
.mb-20 {
  margin-bottom: 20px;
}
.mr-10 {
  margin-right: 10px;
}
.w-150 {
  width: 150px;
}
.overlay {
  display: none;
  position: absolute;
  // top: 65px;
  // right: 350px;
  top: 0px;
  right: 0px;
  bottom: 0;
  left: 0;
  background: #000000;
  mix-blend-mode: multiply;
  opacity: 0.3;
  z-index: 2;
  border-radius: 15px;
}
.size-16 {
  font-size: 16px;
  white-space: nowrap;
}
input[type='number'] {
  text-align: left;
}
</style>

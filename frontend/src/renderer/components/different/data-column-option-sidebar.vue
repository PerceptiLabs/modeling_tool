<template lang="pug">
  header(
    v-if="showIfTypeIs(['image', 'numerical'])"
    :class="{'is-open': isOpen}"
  )
    div.overlay(@click="onCancel")
    main
      perfect-scrollbar
        h4.pre-processing-text Pre-processing for {{columnNames[index]}}
        .main-content
          div.mb-20
            base-checkbox(
              v-if="showIfTypeIs(['image', 'numerical'])"
              v-model="options.normalize.value"
              :styleTypeSecondary="true"
              ) Normalize
            div.mt-10(
              v-if="options.normalize.value"
              class="image-random-option-select d-flex flex-column")
              base-radio.mb-5(:group-name="'normalizeTypeGroup' + elementIndex" value-input="standardization" v-model="options.normalize.type")
                span Standardization
              base-radio(:group-name="'normalizeTypeGroup' + elementIndex" value-input="min-max" v-model="options.normalize.type")
                span Min Max
          template(v-if="showIfTypeIs(['image'])")
            div.mb-20
              base-checkbox(
                v-model="options.random_flip.value" :styleTypeSecondary="true") Random Flip
              div.mt-10(
                v-if="options.random_flip.value"
                class="image-random-option-select d-flex flex-column")
                base-radio.mb-5(:group-name="'randomFlipTypeGroup' + elementIndex" value-input="vertical" v-model="options.random_flip.mode")
                  span Vertical
                base-radio.mb-5(:group-name="'randomFlipTypeGroup' + elementIndex" value-input="horizontal" v-model="options.random_flip.mode")
                  span Horizontal
                base-radio.mb-5(:group-name="'randomFlipTypeGroup' + elementIndex" value-input="both" v-model="options.random_flip.mode")
                  span Both
                .d-flex.align-items-center
                  label.form_label.mr-10.input-label Seed:
                  input.form_input.w-150(type="text" v-model="options.random_flip.seed")
            div.mb-20
              base-checkbox(
                v-model="options.resize.value" :styleTypeSecondary="true") Resize
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
                  div.pl-20.d-flex.flex-column(v-if="options.resize.mode === 'custom'")
                    .d-flex.align-items-center.mb-10
                      label.form_label.mr-10.input-label Width:
                      input.form_input.w-150.text-left(type="number" min="1" v-model="options.resize.width")
                    .d-flex.align-items-center
                      label.form_label.mr-10.input-label Height:
                      input.form_input.w-150.text-left(type="number" min="1" v-model="options.resize.height")
            div.mb-20
              base-checkbox(
                :styleTypeSecondary="true"
                v-model="options.random_rotation.value"
              ) Random rotation
              div.mt-10(class="pl-20 d-flex flex-column" v-if="options.random_rotation.value")
                base-radio.mb-5(:group-name="'randomRotationTypeGroup' + elementIndex" value-input="reflect" v-model="options.random_rotation.fill_mode")
                  span Reflect
                base-radio.mb-5(:group-name="'randomRotationTypeGroup' + elementIndex" value-input="constant" v-model="options.random_rotation.fill_mode")
                  span Constant
                base-radio.mb-5(:group-name="'randomRotationTypeGroup' + elementIndex" value-input="wrap" v-model="options.random_rotation.fill_mode")
                  span Wrap
                base-radio.mb-5(:group-name="'randomRotationTypeGroup' + elementIndex" value-input="nearest" v-model="options.random_rotation.fill_mode")
                  span Nearest
                .d-flex.align-items-center.mb-10(v-if="options.random_rotation.fill_mode === 'constant'")
                  label.form_label.mr-10.input-label Fill:
                  input.form_input.w-150.text-left(type="number" v-model="options.random_rotation.fill_value")
    
                .d-flex.align-items-center.mb-10
                  label.form_label.mr-10.input-label Factor:
                  input.form_input.w-150.text-left(type="number" v-model="options.random_rotation.factor")
                .d-flex.align-items-center.mb-10
                  label.form_label.mr-10.input-label Seed:
                  input.form_input.w-150.text-left(type="number" v-model="options.random_rotation.seed")
            div.mb-20
              base-checkbox(
                :styleTypeSecondary="true"
                v-model="options.random_crop.value"
              ) Random Crop
              div.mt-10.pl-25(
                v-if="options.random_crop.value"
              )
                .d-flex.align-items-center.mb-10
                  label.form_label.mr-10.input-label Seed:
                  input.form_input.w-150(type="text" v-model="options.random_crop.seed")
                .d-flex.align-items-center.mb-10
                  label.form_label.mr-10.input-label Width:
                  input.form_input.w-150.text-left(type="number" min="1" v-model="options.random_crop.width")
                .d-flex.align-items-center.mb-10
                  label.form_label.mr-10.input-label Height:
                  input.form_input.w-150.text-left(type="number" min="1" v-model="options.random_crop.height")
      footer.d-flex.justify-content-end
        button.btn.btn-menu-bar.mr-10(
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
    this.onSave();
  },
  methods: {
    onSave(){
      const saveResponse = {};
      if(this.dataTypeSelected === 'image') {
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
  background: linear-gradient(180deg, #363E51 0%, #000000 225%);
  border-left: 1px solid rgba(97, 133, 238, 0.4);
  border-bottom: 1px solid rgba(97, 133, 238, 0.4);
  top: 0;
  z-index: 10;
  margin-top: 65px;
  height: calc(100% - 65px);
  width: 350px;
}
.main-content {
  padding: 20px;
}

footer {
  margin-top: auto;
  padding: 40px 50px;
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
.input-label {
  font-family: 'Roboto', sans-serif;
  font-size: 14px;
  color: #E1E1E1;
  width: 50px;
}
.form_input {
  background: #222736;
  border-radius: 2px;
  border: 1px solid #5E6F9F;
  height: 36px;
  font-family: Roboto, 'sans-serif';
  font-size: 14px;
  line-height: 16px;
  letter-spacing: 0.02em;
  color: #E1E1E1;
  padding-left: 10px;
  transition: 0.3s;
  &:focus {
    border: 1px solid #B6C7FB;
  }
}
.pre-processing-text {
  padding: 20px;
  font-family: Roboto, 'sans-serif';
  font-weight: 500;
  font-size: 14px;
  line-height: 16px;
  color: #B6C7FB;
  border-bottom: 1px solid #5E6F9F;
  
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
  top: 65px;
  right: 350px;
  bottom: 0;
  left: 0;
  background: #000000;
  mix-blend-mode: multiply;
  opacity: 0.3;
  z-index: 2;
}
</style>

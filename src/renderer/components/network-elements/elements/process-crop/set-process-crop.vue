<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body(
        :class="{'active': tabSelected == 0}"
      )
        .settings-layer
          //.settings-layer_section
            .form_row
              .form_label Data Input:
              .form_input
                triple-input(
                  /:value1="50"
                  /:value2="60"
                  /:value3="10"
                )
          .settings-layer_section.text-center.crop-box
            vue-cropper(
              ref="cropper"
              :img="crop"
              :outputSize="1"
              outputType="png"
              :autoCrop="true"
              :info="true"
              :full="false"
              :canMove="true"
              :canMoveBox="true"
              :fixedBox="false"
              :original="false"
              )
          //.settings-layer_section
            .form_row
              .form_label Reshape data:
              .form_input
                input(type="text")
          .settings-layer_foot
            button.btn.btn--primary(type="button" @click="applySettings") Apply


      .popup_body(
          :class="{'active': tabSelected == 1}"
        )
        settings-code(
          :the-code="coreCode"
        )

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
  import TripleInput    from '@/components/base/triple-input';
  import { VueCropper } from 'vue-cropper';

  export default {
    name: 'SetProcessCrop',
    mixins: [mixinSet],
    components: {
      TripleInput,
      SettingsCode,
      VueCropper
    },
    data() {
      return {
        tabs: ['Settings', 'Code'],
        crop: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Hopetoun_falls.jpg/220px-Hopetoun_falls.jpg",
        option: {
          img: '',
          size: 1,
          full: false,
          outputType: 'png',
          canMove: true,
          fixedBox: false,
          original: false,
          canMoveBox: true
        },
        settings: {
          Offset_height: '0',
          Offset_width: '0',
          Target_height: '16',
          Target_width: '16'
        }
      }
    },
    computed: {
      coreCode() {
        return `
        Y=tf.image.crop_to_bounding_box(X, properties["${this.settings.Offset_height}"], properties["${this.settings.Offset_width}"], properties["${this.settings.Target_height}"], properties["${this.settings.Target_width}"])`
      }
    }
  }
</script>
<style lang="scss">
  @import "../../../../scss/base";
  $w-crop-point: .4rem;
  $h-crop-point: 1.4rem;
  .crop-box {
    height: 291px;
    .cropper-view-box {
      outline: none;
    }
    .cropper-modal {
      background: rgba($bg-workspace, .8);
    }
    .crop-point {
      background-color: $color-5;
      border-radius: 0;
      opacity: 1;
      margin: 0;
    }
    .point1,
    .point3,
    .point6,
    .point8 {
      width: $w-crop-point;
      height: $h-crop-point;
      &:after {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        width: $h-crop-point;
        height: $w-crop-point;
        background-color: $color-5;
      }
    }
    .point3 {
      &:after {
        left: auto;
        right: 0;
      }
    }
    .point6 {
      &:after {
        top: auto;
        bottom: 0;
      }
    }
    .point8 {
      &:after {
        left: auto;
        right: 0;
        top: auto;
        bottom: 0;
      }
    }
    .point4,
    .point5 {
      width: $w-crop-point;
      height: $h-crop-point;
      transform: translateY(-50%);
    }
    .point2,
    .point7 {
      width: $h-crop-point;
      height: $w-crop-point;
      transform: translateX(-50%);
    }
    .point3,
    .point5,
    .point8 {
      right: 0;
    }
    .point1,
    .point4,
    .point6 {
      left: 0;
    }
    .point1,
    .point2,
    .point3 {
      top: 0;
    }
    .point6,
    .point7,
    .point8 {
      bottom: 0;
    }
  }
</style>

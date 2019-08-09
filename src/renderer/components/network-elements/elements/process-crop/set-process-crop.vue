<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
    @press-update="updateCode"
  )
    template(slot="Settings-content")
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

    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        v-model="coreCode"
      )

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import TripleInput    from '@/components/base/triple-input';
  import { VueCropper } from 'vue-cropper';

  export default {
    name: 'SetProcessCrop',
    mixins: [mixinSet],
    components: {
      TripleInput,
      VueCropper
    },
    data() {
      return {
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
      codeDefault() {
        return {
          Output: `Y=tf.image.crop_to_bounding_box(X['Y'], ${this.settings.Offset_height}, ${this.settings.Offset_width}, ${this.settings.Target_height}, ${this.settings.Target_width})`
        }
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

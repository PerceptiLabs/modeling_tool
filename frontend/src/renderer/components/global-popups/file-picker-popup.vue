<template lang="pug">

  .popup-global(ref="popup-container")
    .popup-global_overlay(@click="closePopup()")
    section.popup(ref="popup")
      .popup-close(@click="closePopup()")
        svg(width="8" height="8" viewBox="0 0 8 8" fill="none" xmlns="http://www.w3.org/2000/svg")
          path(fill-rule="evenodd" clip-rule="evenodd" d="M0.165255 0.165255C0.217507 0.112872 0.279579 0.0713107 0.347917 0.0429534C0.416256 0.0145962 0.489517 0 0.563505 0C0.637493 0 0.710755 0.0145962 0.779093 0.0429534C0.847431 0.0713107 0.909504 0.112872 0.961755 0.165255L3.93851 3.14313L6.91526 0.165255C6.96755 0.112956 7.02964 0.0714704 7.09797 0.0431664C7.16631 0.0148624 7.23954 0.000294507 7.31351 0.000294507C7.38747 0.000294507 7.4607 0.0148624 7.52904 0.0431664C7.59737 0.0714704 7.65946 0.112956 7.71176 0.165255C7.76405 0.217554 7.80554 0.279642 7.83384 0.347974C7.86215 0.416306 7.87672 0.489543 7.87672 0.563505C7.87672 0.637467 7.86215 0.710705 7.83384 0.779037C7.80554 0.847369 7.76405 0.909456 7.71176 0.961755L4.73388 3.93851L7.71176 6.91526C7.76405 6.96755 7.80554 7.02964 7.83384 7.09797C7.86215 7.16631 7.87672 7.23954 7.87672 7.31351C7.87672 7.38747 7.86215 7.4607 7.83384 7.52904C7.80554 7.59737 7.76405 7.65946 7.71176 7.71176C7.65946 7.76405 7.59737 7.80554 7.52904 7.83384C7.4607 7.86215 7.38747 7.87672 7.31351 7.87672C7.23954 7.87672 7.16631 7.86215 7.09797 7.83384C7.02964 7.80554 6.96755 7.76405 6.91526 7.71176L3.93851 4.73388L0.961755 7.71176C0.909456 7.76405 0.847369 7.80554 0.779037 7.83384C0.710705 7.86215 0.637467 7.87672 0.563505 7.87672C0.489543 7.87672 0.416306 7.86215 0.347974 7.83384C0.279642 7.80554 0.217554 7.76405 0.165255 7.71176C0.112956 7.65946 0.0714704 7.59737 0.0431664 7.52904C0.0148624 7.4607 0.000294507 7.38747 0.000294507 7.31351C0.000294507 7.23954 0.0148624 7.16631 0.0431664 7.09797C0.0714704 7.02964 0.112956 6.96755 0.165255 6.91526L3.14313 3.93851L0.165255 0.961755C0.112872 0.909504 0.0713107 0.847431 0.0429534 0.779093C0.0145962 0.710755 0 0.637493 0 0.563505C0 0.489517 0.0145962 0.416256 0.0429534 0.347917C0.0713107 0.279579 0.112872 0.217507 0.165255 0.165255Z")

      .popup-background
        h1.popup-title.bold.text-center {{popupTitle}}
        .popup_body
          file-picker(
            :filePickerType="filePickerType"
            :fileTypeFilter="fileTypeFilter"
            :options="filePickerOptions"
            :startupFolder="startupFolder"
            :confirmCallback="confirmCallback"
            :cancelCallback="closePopup")
          
</template>

<script>
import Moveable from "moveable";
import FilePicker from '@/components/different/file-picker.vue';

export default {
  name: "FilePickerPopup",
  components: { FilePicker, Moveable },
  props: {
    filePickerType: {
      type: String,
      default: 'folder' // can also be 'folder'
    },
    fileTypeFilter: {
      type: Array,
      default: () => []
    },
    confirmCallback: {
      type: Function,
      default: () => {}
    },
    cancelCallback: {
      type: Function,
      default: null
    },
    startupFolder: {
      type: String,
      default: ''
    },
    popupTitle: {
      type: String,
      default: "Select a file/folder"
    },
    options: {
      type: Object,
      default: () => {},
    }
  },
  data() {
    return {
      moveable: '',
      filePickerOptions: {
        showBackButton: false,
        showNumberSelectedFiles: false,
        ...this.options,
      }
    }
  },
  methods: {
    closePopup() {
      if (!this.cancelCallback || typeof this.cancelCallback !== 'function') {
        this.$store.commit('globalView/set_filePickerPopup', false);
      } else {
        this.cancelCallback();
      }
    },
  },
  mounted() {
    // this.moveable = new Moveable(this.$refs['popup-container'], 
    // {
    //     target: this.$refs['popup'],
    //     draggable: true,
    //     keepRatio: true,
    //     throttleDrag: 0,
    //     origin: false,
    // });

    // this.moveable
    // .on("drag", ({ target, transform}) => {
    //   target.style.transform = transform;
    // });
  }
}
</script>

<style lang="scss" scoped>
/deep/ .moveable-control-box {
  .moveable-line {
    display:none; 
  }
}

</style>

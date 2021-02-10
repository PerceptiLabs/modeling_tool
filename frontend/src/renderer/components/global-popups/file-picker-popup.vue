<template lang="pug">

  .popup-global(ref="popup-container")
    .popup-global_overlay(@click="closePopup()")
    section.popup(ref="popup")
      .popup-background
        .popup_tab-set
          .popup_header
            h3 {{ popupTitle }}
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
        this.$store.commit('globalView/HIDE_allGlobalPopups');
      } else {
        this.cancelCallback();
      }
    },
  },
  mounted() {
    this.moveable = new Moveable(this.$refs['popup-container'], 
    {
        target: this.$refs['popup'],
        draggable: true,
        keepRatio: true,
        throttleDrag: 0,
        origin: false,
    });

    this.moveable
    .on("drag", ({ target, transform}) => {
      target.style.transform = transform;
    });
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

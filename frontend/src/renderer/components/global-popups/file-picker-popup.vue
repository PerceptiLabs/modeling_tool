<template lang="pug">

  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup_tab-set
        .popup_header
            h3 {{ popupTitle }}
      .popup_body
        file-picker(
            :filePickerType="filePickerType"
            :options="filePickerOptions"
            :confirmCallback="confirmCallback"
            :cancelCallback="closePopup")
        
</template>

<script>
import { pathSlash }  from '@/core/constants.js';
import FilePicker from '@/components/different/file-picker.vue';

export default {
    name: "FilePickerPopup",
    components: { FilePicker },
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
    },
    data() {
    return {
        popupTitle: 'Export as',
        filePickerOptions: {
            showBackButton: false,
            showNumberSelectedFiles: false,
        }
    }
    },
    methods: {
        closePopup() {
            this.$store.commit('globalView/HIDE_allGlobalPopups');
        },
    }
}
</script>

<style lang="scss" scoped>
</style>

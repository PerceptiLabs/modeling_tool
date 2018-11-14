import fs from 'fs';
import {remote} from 'electron'



import TheToolbar   from '@/components/the-toolbar.vue'
import TheLayersbar from '@/components/the-layersbar.vue'
import TheSidebar   from '@/components/the-sidebar.vue'
import TheWorkspace from '@/components/workspace/the-workspace.vue'
import TheInfoPopup from "@/components/global-popups/the-info-popup";

export default {
  name: 'pageQuantum',
  components: {
    TheToolbar,
    TheLayersbar,
    TheSidebar,
    TheWorkspace,
    TheInfoPopup
  },
  mounted() {
    let dragged;
    let outClassName = 'network-field';
    this.$refs.layersbar.addEventListener("dragstart", ( event )=> {
      if ( event.target.draggable) {
        // console.log(event)
        // console.log('dragstart')
        dragged = event.target;
        this.$store.commit('mod_workspace/ADD_dragElement', event)
        //make it half transparent
        event.target.style.opacity = .75;
      }
    }, false);

    this.$refs.layersbar.addEventListener("dragend", function( event ) {
      // reset the transparency
      //if ( event.target.className == "js-layersbar-draggable" ) {
      //console.log('dragend')
      //console.log(event)
      event.target.style.opacity = "";
      //}
    }, false);

    /* events fired on the drop targets */
    this.$refs.layersbar.addEventListener("dragover", function( event ) {
      event.preventDefault();
    }, false);

    this.$refs.layersbar.addEventListener("dragenter", function( event ) {
      if ( event.target.className.includes(outClassName) ) {
        //event.target.style.cursor = "auto";
        //console.log('dragenter')
      }

    }, false);

    this.$refs.layersbar.addEventListener("dragleave", function( event ) {
      if ( event.target.className.includes(outClassName)) {
        //console.log('dragleave')
        //event.target.style.cursor = "not-allowed";
      }
    }, false);

    this.$refs.layersbar.addEventListener("drop", ( event )=> {
      event.preventDefault();
      if ( event.target.className.includes(outClassName) ) {
        this.$store.commit('mod_workspace/ADD_elToWorkspace', event)
      }
    }, false);
  },
  computed: {
    infoText() {
      return this.$store.state.globalView.globalPopup.showInfoPopup
    },
    eventLoadFile() {
      return this.$store.state.mod_events.openFile
    }
  },

  watch: {
    eventLoadFile() {
      //this.openFileDialog(".js", false);
      this.openDialog()
    }
  },
  methods: {
    openDialog() {
      //console.log(dialog);
      let dialog = remote.dialog;
      dialog.showOpenDialog()
    },
    openFileDialog (accept, multi) {

      var inputElement = document.createElement("input");
      inputElement.type = "file";
      inputElement.accept = accept; // Note Edge does not support this attribute
      if (multi) {
        inputElement.multiple = multi;
      }
      console.log(inputElement);
      inputElement.addEventListener("change", this.fileDialogChanged);

      inputElement.dispatchEvent(new MouseEvent("click"));
    },
    fileDialogChanged (event) {
      console.log(event);
      // fs.readFile(__filename, function(err, data){
      //   if(err){
      //     console.error(err);
      //   }else{
      //     console.log(data);
      //   }
      // });
    },
  }
}

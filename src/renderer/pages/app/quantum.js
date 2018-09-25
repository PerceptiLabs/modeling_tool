import TheToolbar from '@/components/the-toolbar.vue'
import TheLayersbar from '@/components/the-layersbar.vue'
import TheSidebar from '@/components/the-sidebar.vue'
import TheWorkspace from '@/components/workspace/the-workspace.vue'

export default {
  name: 'pageQuantum',
  components: {
    TheToolbar,
    TheLayersbar,
    TheSidebar,
    TheWorkspace
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
}

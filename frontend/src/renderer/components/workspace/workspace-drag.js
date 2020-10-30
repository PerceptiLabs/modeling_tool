
import { mapGetters } from 'vuex';

const workspaceDrag = {
  mounted() {
    document.addEventListener('mousedown', this.mouseDownHandler);
    document.addEventListener('mouseup', this.mouseUpHandler);
  },
  beforeDestroy() {
    document.removeEventListener('mousedown', this.mouseDownHandler);
    document.removeEventListener('mouseup', this.mouseUpHandler);
  },
  data() {
    return {
      initialX: null,
      initialY: null,
      initialScrollLeft: null,
      initialScrollTop: null,
      isDragInitialCordSetted: false,
    }
  },
  computed: {
    ...mapGetters({
      getIsWorkspaceDragEvent: 'mod_events/getIsWorkspaceDragEvent',
    })
  },
  methods: {
    mouseDownHandler(ev){
      ev.preventDefault();
      if(ev.ctrlKey || ev.metaKey || ev.button === 1) {
        document.addEventListener('mousemove', this.onMouseMove);
      }
    },
    mouseUpHandler() {
      document.removeEventListener('mousemove', this.onMouseMove);
      this.resetToInitialSetup();
    },
    setInitailDragPosition(clientX, clientY) {
      this.clientX = clientX;
      this.clientY = clientY;
    },
    onMouseMove(ev) {
      ev.preventDefault();

      const networkWorkspace = document.getElementById('networkWorkspace');

      if(!this.isDragInitialCordSetted) {
        if(!this.getIsWorkspaceDragEvent) {
          this.$store.commit('mod_events/set_isWorkspaceDragEvent', true);
        }
        this.setInitailDragPosition(ev.clientX, ev.clientY);
        this.initialScrollLeft = networkWorkspace.scrollLeft;
        this.initialScrollTop = networkWorkspace.scrollTop;
        this.isDragInitialCordSetted = true;
      } 

      networkWorkspace.scrollLeft = this.initialScrollLeft + (this.clientX - ev.clientX)
      networkWorkspace.scrollTop = this.initialScrollTop + (this.clientY - ev.clientY)
    },
    resetToInitialSetup() {
      if(this.getIsWorkspaceDragEvent) {
        this.$store.commit('mod_events/set_isWorkspaceDragEvent', false);
      }
      this.setInitailDragPosition(null, null);
      this.initialScrollLeft = null;
      this.initialScrollTop = null;
      this.isDragInitialCordSetted = false;
    }
  }
};

export default workspaceDrag;
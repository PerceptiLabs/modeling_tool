
import { mapGetters } from 'vuex';

const workspaceDrag = {
  mounted() {
    const el = document.getElementById('networkWorkspace');
    if(el) {
      el.addEventListener('mousedown', this.mouseDownHandler);
    }
    
    document.addEventListener('mouseup', this.mouseUpHandler);
  },
  beforeDestroy() {
    const el = document.getElementById('networkWorkspace');
    if(el) {
      el.removeEventListener('mousedown', this.mouseDownHandler);
    }
    
    document.removeEventListener('mouseup', this.mouseUpHandler);
  },
  data() {
    return {
      initialX: null,
      initialY: null,
      initialScrollLeft: null,
      initialScrollTop: null,
      isDragInitialCordSet: false,
    }
  },
  computed: {
    ...mapGetters({
      getIsWorkspaceDragEvent: 'mod_events/getIsWorkspaceDragEvent',
    })
  },
  methods: {
    mouseDownHandler(ev){
      if(ev.ctrlKey || ev.metaKey || ev.button === 1) {
        const el = document.getElementById('networkWorkspace');
        document.addEventListener('keyup', this.mouseUpHandler);
        el.addEventListener('mousemove', this.onMouseMove);
      }
    },
    mouseUpHandler() {
      const el = document.getElementById('networkWorkspace');
      el.removeEventListener('mousemove', this.onMouseMove);
      document.removeEventListener('keyup', this.mouseUpHandler);
      this.$store.commit('mod_events/set_eventComponentDrop');
      this.resetToInitialSetup();
    },
    setInitialDragPosition(clientX, clientY) {
      this.clientX = clientX;
      this.clientY = clientY;
    },
    onMouseMove(ev) {
      ev.preventDefault();

      const networkWorkspace = document.getElementById('networkWorkspace');

      if(!this.isDragInitialCordSet) {
        if(!this.getIsWorkspaceDragEvent) {
          this.$store.commit('mod_events/set_isWorkspaceDragEvent', true);
        }
        this.setInitialDragPosition(ev.clientX, ev.clientY);
        this.initialScrollLeft = networkWorkspace.scrollLeft;
        this.initialScrollTop = networkWorkspace.scrollTop;
        this.isDragInitialCordSet = true;
      } 

      networkWorkspace.scrollLeft = this.initialScrollLeft + (this.clientX - ev.clientX)
      networkWorkspace.scrollTop = this.initialScrollTop + (this.clientY - ev.clientY)
    },
    resetToInitialSetup() {
      if(this.getIsWorkspaceDragEvent) {
        this.$store.commit('mod_events/set_isWorkspaceDragEvent', false);
      }
      this.setInitialDragPosition(null, null);
      this.initialScrollLeft = null;
      this.initialScrollTop = null;
      this.isDragInitialCordSet = false;
    }
  }
};

export default workspaceDrag;
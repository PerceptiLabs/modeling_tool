<template lang="pug">
  div(:style="workspaceMiniMapWrapperStyle"
    @mousedown="handleMouseDown" 
    @mouseup="handleMouseUp" 
    @mousemove="handleMouseOver"
    @mouseleave="handleMouseUp"
    v-if="isMiniMapNavigatorOpened"
    ref="miniMap"
    data-testing-target="mini-map"
    )
    div.mini-map-relative-wrapper(:style="miniMapRelativeWrapperStyles")
      div.close-mini-map-position
        button.close-mini-map(@click="closeMiniMapNavigation")
      network-field(
        ref="networkField"
        :scaleNet="1"
        :key="this.currentNetworkIndex"
        :style="workspaceMiniMapStyle"
        :isViewMode="true"
      )
      div.box-outline(:style="boxOutlineStyles")
</template>
<script>
  import { mapGetters, mapState, mapMutations } from 'vuex';
  import NetworkField from '@/components/network-field/network-field.vue'
  export default {
    name: 'mini-map-navigation',
    components: {NetworkField},
    data() {
      return {
        isMouseDown: false,
        workspaceMiniMapStyle: {},
        workspaceMiniMapWrapperStyle: {},
        miniMapRelativeWrapperStyles: {},
        boxOutlineStyles: {}
      }
    },
    props: {
      scaleNet: {
        type: Number,
        default: 100,
      },
    },
    computed: {
      ...mapGetters({
        currentNetworkList: 'mod_workspace/GET_currentNetworkElementList',
      }),
      ...mapState({
        currentNetworkIndex: state => state.mod_workspace.currentNetwork,
        workspace: state => state.mod_workspace.workspaceContent,
        isMiniMapNavigatorOpened: state => state.globalView.isMiniMapNavigatorOpened,
        sidebarState:             state => state.globalView.hideSidebar,
      }),
      netPosition() {
        // return  Object.values(this.currentNetworkList).map(itm => itm.layerMeta.position.top + '-' + itm.layerMeta.position.left);
        return  Object.values(this.currentNetworkList).map(itm => ([itm.layerMeta.position.top, itm.layerMeta.position.left]));
      }
    },
    watch: {
      sidebarState() {
        setTimeout(this.updateAllStyles, 300);
      },
      scaleNet() {
        this.updateAllStyles();
        setTimeout(() => this.updateAllStyles())
      },
      netPosition(currentValues, prevValues) {
        const parentWorkspace = document.getElementById('networkWorkspace');
        const { offsetWidth, scrollHeight, offsetHeight } = parentWorkspace;
        
        const previousMaxWidth = Math.max(...prevValues.map(itm => itm[1]));
        const currentMaxWidth= Math.max(...currentValues.map(itm => itm[1]));

        const previousMaxHeight = Math.max(...prevValues.map(itm => itm[0]));
        const currentMaxHeight = Math.max(...currentValues.map(itm => itm[0]));
        
        if(currentMaxWidth < previousMaxWidth) {
          
          parentWorkspace.scrollLeft = currentMaxWidth - offsetWidth + 70;
        }
        if(currentMaxHeight < previousMaxHeight) {
          parentWorkspace.scrollTop = currentMaxHeight - offsetHeight + 70;
        }
        
       
        this.updateAllStyles();
      },
      isMiniMapNavigatorOpened() {
        this.$nextTick(function () {
          this.updateAllStyles();
        })
      }
    },
    mounted() {
      this.updateWorkspaceMiniMapStyles();
      this.updateMiniMapRelativeWrapperStyles();
      this.updateWorkspaceMiniMapWrapperStyling();
      this.updateBoxOutlineStyles();
      setTimeout(() => this.updateAllStyles());
      const networkWorkspace = document.getElementById('networkWorkspace');
      if (networkWorkspace) { 
        networkWorkspace.addEventListener('scroll', this.updateBoxOutlineStyles);
      }
      window.addEventListener('resize', this.updateBoxOutlineStyles);
      
    },
    destroyed() {
      const networkWorkspace = document.getElementById('networkWorkspace');
      if (networkWorkspace) { 
        networkWorkspace.removeEventListener('scroll', this.updateBoxOutlineStyles);
      }
      window.removeEventListener('resize', this.updateBoxOutlineStyles);
      clearTimeout(this.updateAllStyles);
    },
    methods: {
      ...mapMutations({
        setMiniMapNavigationMutation: 'globalView/setMiniMapNavigationMutation',
      }),
      getScaleForMiniMap() {
        const el = document.getElementsByClassName('network-field')[0];
        if(!el) return {w: 0, h: 0, width: 0, height: 0};
        return {
          width: el.scrollWidth,
          height: el.scrollHeight,
          w: (230 / (Math.max(el.scrollWidth,el.scrollHeight) / 100)) / 100,
          h: (134 / (Math.max(el.scrollWidth,el.scrollHeight) / 100)) / 100,
        }
      },
      updateWorkspaceMiniMapWrapperStyling() {
        this.workspaceMiniMapWrapperStyle =  {
          // display: this.isMiniMapNavigatorOpened ? 'block' : 'none',
          cursor: !!this.isMouseDown ? 'grab' : 'pointer',
          position: 'absolute',
          zIndex: 2,
          bottom: '20px',
          left: '20px',
        }
      },
      updateMiniMapRelativeWrapperStyles(){
        const { height, width, w } = this.getScaleForMiniMap();
        this.miniMapRelativeWrapperStyles = {
          cursor: !!this.isMouseDown ? 'grab': 'pointer',
          height: (height * w) + 'px',
          width: (width * w) + 'px',
          // backgroundColor: 'rgba(0, 0, 0, 0.9)',
          boxSizing: 'content-box',
          border: '1px solid #383F50',
          borderTopWidth: '16px',
          background: '#23252A',
        }
      },
      updateWorkspaceMiniMapStyles() {
        const el = document.getElementsByClassName('network-field')[0];
        const { w } = this.getScaleForMiniMap();
        const scale = w;

        this.workspaceMiniMapStyle = {
          bottom: '0',
          left: '0',
          position: 'absolute',
          width: el ? el.scrollWidth + 'px' : '1600px',
          height: el ? el.scrollHeight + 'px' : '600px',
          transformOrigin: 'left bottom',
          transform: `scale(${scale})`,
        }
      },
      
      handleMouseDown(e) {
        this.isMouseDown = true;
        if(e.target.nodeName === 'BUTTON') return; // prevent changing map position when map is closed
        this.minMapToMapPosition(e);
      },
      handleMouseUp() {
        this.isMouseDown = false;
        this.updateAllStyles();
      },
      handleMouseOut() {
        this.isMouseDown = false;
        this.updateAllStyles();
      },
      handleMouseOver(e) {
        if(this.isMouseDown) {
          this.minMapToMapPosition(e);
        }
      },
      minMapToMapPosition(e) {
        const { offsetX, offsetY } = e;
        const { w, height, width } = this.getScaleForMiniMap();
        const parentWorkspace = document.getElementById('networkWorkspace');
        const { scrollWidth, offsetWidth, scrollHeight, offsetHeight } = parentWorkspace;
        const leftClickInPercent = offsetX / (width / 100);
        const topClickInPercent = offsetY / (height / 100);
        
        const left = ((scrollWidth / 100) * leftClickInPercent) - (offsetWidth / 2);
        const top = ((scrollHeight / 100) * topClickInPercent) - (offsetHeight / 2);

        parentWorkspace.scrollLeft = left;
        parentWorkspace.scrollTop = top;
      },
      updateBoxOutlineStyles() {
        this.updateWorkspaceMiniMapStyles();
        this.updateMiniMapRelativeWrapperStyles();
        this.updateWorkspaceMiniMapWrapperStyling();
        const { w, h, height } = this.getScaleForMiniMap();
        let scale = this.scaleNet / 100;

        const parentWorkspace = document.getElementById('networkWorkspace');
        if (parentWorkspace) {
          const { scrollWidth, offsetWidth, scrollLeft, scrollHeight, offsetHeight, scrollTop } = parentWorkspace;
          const shouldShowBox = scrollWidth <= offsetWidth && scrollHeight <= offsetHeight;
          this.boxOutlineStyles = {
            display: shouldShowBox ? 'none': 'block',
            // width: ((offsetWidth) * w) / scale + 'px',
           
            maxWidth: '100%',
            maxHeight: '100%',
            width: ((offsetWidth) * w) + 'px',
            height: ((offsetHeight) * w) + 'px',
            left: ((scrollLeft) * w) + 'px',
            top: ((scrollTop) * w) + 'px',
            zIndex: 15
          }
        }
      },
      updateAllStyles() {
        this.updateWorkspaceMiniMapStyles();
        this.updateMiniMapRelativeWrapperStyles();
        this.updateWorkspaceMiniMapWrapperStyling();
        this.updateBoxOutlineStyles();
      },
      closeMiniMapNavigation(e) {
        e.preventDefault();
        this.setMiniMapNavigationMutation(false);
      }
    }
  }
</script>
<style lang="scss">
  .mini-map-relative-wrapper {
    width: 160px;
    height: 100px;

    position: relative;
    &:after {
      position: absolute;
      z-index: 2;
      content: '';
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
    }
  }
  .box-outline {
    z-index: 2;
    position: absolute;
    border: 1px solid red;
    pointer-events: none;
  }
  .close-mini-map-position {
    position: absolute;
    right: 3px;
    top: -18px;
    width: 10px;
    height: 10px;
  }
  .close-mini-map {
    position: relative;
    background: none;
    padding: 6px;
    &:after, &:before {
      z-index: 3;
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      width: 7px;
      height: 1px;
      border-radius: 1px;
      background-color: #fff;
      transform-origin: 50% 50%;
    }
    &:after {
      transform: translate(-50%, -50%) rotate(-45deg);
    }
    &:before {
      transform: translate(-50%, -50%) rotate(45deg);
    }
  }
</style>
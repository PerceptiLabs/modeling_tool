<template lang="pug">
  main.page_workspace(
    :class="{'open-statistics': statisticsIsOpen}"
  )
    empty-navigation(v-if="emptyNavigationMode!=0")
    .workspace_tabset(
      ref="tabset"
      v-if="emptyNavigationMode==0"
    )
      include ./tabset/workspace-tabset.pug
    component.blue-left-border(:is="toolbarType" v-if="emptyNavigationMode==0")
    .workspace_content.bookmark_content.js-workspace.blue-border(
      v-show="emptyNavigationMode==0"  
      ref="workspaceNet"
      :class="{'workspace-relative' : showTrainingSpinner, 'open-statistics': statisticsIsOpen, 'is-drag-active': getIsWorkspaceDragEvent}"
      )
      .network(
        v-if="currentNetworkIndex === i"
        v-for="(net, i) in workspace"
        :key="net.networkID"
        :class="networkClass"
      )
        the-view-box#tutorial_statistics.the-statistics(
          v-if="statisticsIsOpen"
          :el-data="statisticsElSelected.statistics"
          :data-tutorial-target="'tutorial-test-right-chart'"
          section-title="Statistics"
        )
        the-view-box#tutorial_view-box.the-view-box(
          v-if="statisticsIsOpen"
          :el-data="statisticsElSelected.viewBox"
          :data-tutorial-target="'tutorial-test-left-chart'"
          section-title="ViewBox"
          )
        section.network_info-section.the-network-field(
          ref="networkWindow"
          )
          .info-section_head(v-if="statisticsIsOpen")
            h3 Map
          .spinner-container(v-if="showTrainingSpinner && isStatisticsOrTestOpened")
            chart-spinner
          perfect-scrollbar.info-section_main.js-info-section_main(
            @wheel="scaleScroll($event)"
            id="networkWorkspace"
            v-if="!showTrainingSpinner || !isStatisticsOrTestOpened"
            )
            network-field(
              ref="networkField"
              :key="i"
              :scaleNet="scaleNet"
            )
            // when select more then 2 network item its display
            div(:style="dragBoxHorizontalTopBorder()")
            div(:style="dragBoxHorizontalBottomBorder()")
            div(:style="dragBoxVerticalLeftBorder()")
            div(:style="dragBoxVerticalRightBorder()")
          mini-map-navigation(:scaleNet="scaleNet")
          //- sidebar-layers.layers-sidebar
        code-window(
          v-if="showCodeWindow"
          :networkId="currentNetworkId"
          :data-tutorial-target="'tutorial-workspace-settings-code'"
        )
        //- notifications-window(
        //-   v-if="showNotificationWindow"
        //- )
        information-panel(
          v-if="showNotificationWindow"
        )
        //-general-settings(v-if="showGlobalSet")
        general-result(v-if="showGlobalResult")
        select-core-side(v-if="showCoreSide")
        workspace-before-import(v-if="showWorkspaceBeforeImport")
        workspace-load-network(
          v-if="showLoadSettingPopup" 
        )

        the-toaster(:style="toasterRightPosition")
    .hardware-metrics(
      v-show="showResourceView!=0 && statisticsIsOpen"
      ) 
      .header
        h4 RAM/CPU/GPU
        i.icon.icon-app-minimize.btn.btn--icon(type="button"
          @click="setResourceView(0)"
        ) 
      .resource-wrapper
        resource-monitor(
          :monitor-value="currentData"
          v-show="showResourceView>0"
        )
      .labels
        .row_item
          .ticker.red
          span RAM
        .row_item
          .ticker.yellow
          span CPU
        .row_item
          .ticker.green
          span GPU

    .workspace_footer(
      v-if="emptyNavigationMode===0"
      )
      include ./footer/workspace-footer.pug

    workspace-save-network(
      v-if="showSaveNetworkPopup"
      ref="saveNetworkPopup"
      :popup-settings="saveNetworkPopup"
      )
    export-network(v-if="showExportNetworkPopup")
    export-network-git-hub(v-if="showExportNetworkToGitHubPopup")
    import-model(v-if="showImportNetworkfromGitHubOrLocalPopup")

    .select-modal-wrapper(
      v-if="showNewModelPopup"
      )
      select-model-modal(
        class="select-model-modal"
        v-if="showNewModelPopup"
        @close="onCloseSelectModelModal"
        )
    global-training-settings(v-if="isGlobalTrainingSettingsPopupOpened")
</template>

<script src="./the-workspace.js"></script>

<style lang="scss" scoped>
  @import "../../scss/base";
  @import "./tabset/workspace-tabset";
  @import "./footer/workspace-footer";
  
  .select-modal-wrapper {
    position: absolute;
    width: calc(100% - 46px);
    height: calc(100% - 40px);
    background: rgba(33, 40, 57, 0.9);
    z-index: 99;
  }
  .select-model-modal {
    z-index: 100;
  }
  .page_workspace {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    width: 100%;
    height: 100%;

    &.open-statistics {
      position: relative;
    }
  }
  .workspace_tabset {
    flex: 0 0 auto;
    padding-top: 0.5rem;
    display: flex;
    justify-content: flex-start;
    align-items: flex-end;
    background-color: $bg-workspace;
    border-bottom: 1px solid $toolbar-separator-color;

    .tab-group {
      display: flex;
    }
  }
  .workspace_content {
    display: flex;
    flex: 1 1 100%;
    overflow: hidden;
    &.is-drag-active {
      cursor: grab;
    }
    &.open-statistics {
      z-index: 3;      
      background: transparent;

      &.workspace-relative {
        z-index: 1;
      }

      .network_info-section.tutorial-relative.the-statistics {
        background: transparent;
      }
    }
  }
  .network {
    position: relative;
    width: 100%;
    display: grid;
    grid-template-areas:  'network-field   network-field'
                          'network-field    network-field';
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    &.open-statistic {
      grid-template-areas:  'the-statistics   the-statistics'
                            'network-field  view-box';
    }
  }
  .network--show-code {
    transform: translate(0);
  }
  .the-statistics {
    grid-area: the-statistics;
  }
  .the-view-box {
    grid-area: view-box;
  }
  .the-testing {
    grid-area: the-testing;
  }
  .the-network-field {
    grid-area: network-field;
    background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
    border: 1px solid rgba(97, 133, 238, 0.4);
  }
  .layers-sidebar {
    position: fixed;
    right: 2rem;
    transform: translateY(2rem);
  }

  .network_info-section {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: $bg-workspace-3;

    > .info-section_head {
      background: #090f19;
    }
  }
  .info-section_main {
    display: block;
    overflow: auto;
  }
 
  .workspace-relative {
    position: relative;
  }
  
  .hardware-metrics {
    z-index: 10;
    border-radius: 2px;
    border: 1px solid #5E6F9F;
    width: 374px;
    height: 200px;
    background: #222939;
    position: absolute;
    bottom: 31px;
    right: 2px;

    .resource-wrapper {
      position: absolute;
      top: 35px;
      left: 5px;
      right: 5px;
      z-index: 10;
      width: 300px;
      height: calc(100% - 45px);
    }

    .labels {
      position: absolute;
      right: 15px;
      top: 42px;
      
      .row_item {
        display: flex;
        margin-bottom: 10px;
        align-items: center;
      }

      .ticker {
        width: 15px;
        height: 4px;
        border-radius: 2px;
        margin-right: 8px;

        &.red {
          background: #FE7373;
        }
        &.yellow{
          background: #F7D081
        }
        &.green{
          background: #73FEBB
        }
      }
    }

    .header {
      color: #B6C7FB;
      background: #090f19;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid #5E6F9F;
      width: 100%;
      height: 25px;
      padding: 0px 7px;
      margin: 0;

      h4 {
        margin: 0;
      }

      i {
        font-size: 7px;
        
        &:hover {
          cursor: pointer;
        }
      }
    }
  }

  .statistics-tabs {
    margin-left: auto;
  }
  .blue-border {
   border: 1px solid rgba(97, 133, 238, 0.4);
  }
  .blue-left-border {
   border: 1px solid rgba(97, 133, 238, 0.4);
  }
  .spinner-container {
    position: relative;
    height: 100%;
  }
</style>

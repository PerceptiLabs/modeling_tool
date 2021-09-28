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
      .action_tab(v-if="!statisticsIsOpen")
        button.btn.btn--normal.btn--save(@click="saveNetworkEvent")
          svg.icon(width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg")
            g(clip-path="url(#clip0)")
              path(d="M16.3776 2.56511L14.4349 0.622393C14.0364 0.223855 13.4959 0 12.9323 0H11.6875V3.71875C11.6875 4.01213 11.4496 4.25 11.1562 4.25H2.65625C2.36287 4.25 2.125 4.01213 2.125 3.71875V0H1.0625C0.475734 0 0 0.475668 0 1.0625V15.9375C0 16.5243 0.475734 17 1.0625 17H15.9375C16.5243 17 17 16.5243 17 15.9375V4.06771C17 3.50409 16.7761 2.96361 16.3776 2.56511ZM14.875 14.875H2.125V8.5H14.875V14.875Z" fill="#6185EE")
              path(d="M9.5625 0H7.4375V3.1875H9.5625V0Z" fill="#6185EE")
            defs
              clipPath(id="clip0")
                rect(width="17" height="17" fill="white")
          span Save
        //- button(v-if="modelTrainingSettings && isGlobalTrainingSettingEnabled" @click="onOffBtn(true)").btn.btn--secondary
        //-   | Run with current settings
        button.btn.btn--secondary(type="button" @click="openDataSettings")
          span Data Settings
        button#tutorial_run-training-button.btn.btn--primary(type="button"
          :class="statusStartBtn"
          :data-tutorial-target="'tutorial-workspace-start-training'"
          @click="onOffBtn(false)"
        )
          img(v-if="showSpinnerOnRun===true" src="static/img/spinner.gif" width="12px" style="margin-right: 5px")
          i.icon.icon-on-off(v-if="showSpinnerOnRun===false")
          span(v-html="statusTraining === 'training' || statusTraining === 'pause' ? 'Stop' : 'Run'")


    .workspace-frame(:class="{'border':emptyNavigationMode==0}")
      component.blue-left-border(:is="toolbarType" v-if="emptyNavigationMode==0")    
      .workspace_content_wrapper
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
            workspace-load-network(v-if="showLoadSettingPopup")

            the-toaster(:style="toasterRightPosition")
        the-sidebar(v-if="getViewType==='model' && emptyNavigationMode===0")
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
      dataset-settings-popup(v-if="showDatasetSettingsPopup")
</template>

<script src="./the-workspace.js"></script>

<style lang="scss" scoped>
  
  @import "./tabset/workspace-tabset";
  @import "./footer/workspace-footer";
  
  .select-modal-wrapper {
    position: absolute;
    width: calc(100% - #{$w-sidemenu});
    height: calc(100% - #{$h-header-win});
    background: $bg-window;
    border-radius: 15px 0 0 0;
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
    border-radius: 15px 0 0 0;
    padding: 10px 20px;
    background-color: theme-var($neutral-7);

    &.open-statistics {
      position: relative;
    }
  }
  .workspace_tabset {
    flex: 0 0 auto;
    margin-bottom: 10px;
    display: flex;
    // justify-content: flex-start;
    justify-content: space-between;
    align-items: flex-end;
    // background-color: $bg-workspace;
    // border-bottom: 1px solid $toolbar-separator-color;

    .tab-group {
      display: flex;
    }
  }
  .workspace-frame {
    background: theme-var($neutral-8);
    border-radius: 4px;

    &.border {
      border: $border-1;
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
    
    &:not(.open-statistics) {
      & .the-network-field {
        border-radius: 0px;
        border-width: 0px;
      }
    }
  }
  .network {
    position: relative;
    width: 100%;    
    height: calc(100vh - #{$remaining});
    display: grid;
    grid-template-areas:  'network-field   network-field'
                          'network-field    network-field';
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    &.open-statistic {
      height: calc(100vh - #{$remaining});
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
    margin: 4px;
    border: $border-1;    
    border-radius: 4px;
  }
  .the-testing {
    grid-area: the-testing;
  }
  .the-network-field {
    grid-area: network-field;
    // background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
    border: $border-1;
    border-radius: 4px;

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
      color: $color-6;
      // background: #090f19;
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
    background: theme-var($neutral-8);
    border: $border-1;
    border-radius: 4px;
    width: 374px;
    height: 270px;
    position: absolute;
    bottom: 58px;
    right: 20px;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3);

    .resource-wrapper {
      position: absolute;
      top: 78px;
      left: 5px;
      right: 5px;
      z-index: 10;
      width: 300px;
      height: calc(100% - 80px);
    }

    .labels {
      position: absolute;
      right: 15px;
      top: 82px;
      
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
      color: $color-6;
      background: theme-var($neutral-7);
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: $border-1;
      width: 100%;
      padding: 10px 15px;
      margin: 0;

      h4 {
        margin: 0;
      }

      i {
        font-size: 12px;
        
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
   // border: 1px solid rgba(97, 133, 238, 0.4);
  }
  .blue-left-border {
   // border: 1px solid rgba(97, 133, 238, 0.4);
  }
  .spinner-container {
    position: relative;
    height: 100%;
  }
  .workspace_content_wrapper {
    display: flex;
    overflow: hidden;
  }
  
  .action_tab {
    display: flex;
    align-items: center;
    margin: 0;

    & > button:not(:first-child) {
      margin-left: 2rem;
    }
  }

  .btn--save {
    color: $color-6;
  }
</style>

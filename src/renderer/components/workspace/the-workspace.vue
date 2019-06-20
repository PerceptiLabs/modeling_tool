<template lang="pug">
  main.page_workspace
    .workspace_tabset
      include ./tabset/workspace-tabset.pug
    .workspace_content.bookmark_content.js-workspace(
      ref="workspaceNet" :class="{'workspace-relative' : showTrainingSpinner}"
      )
      start-training-spinner(:showSpinner="showTrainingSpinner")
      .network(
        v-if="indexCurrentNetwork === i"
        v-for="(net, i) in workspace"
        :key="net.networkID"
        :class="networkClass"
      )
        the-testing.the-testing(v-if="testIsOpen")
        the-statistics.the-statistics(
          v-if="statisticsIsOpen || testIsOpen"
          :el-data="statisticsElSelected.statistics"
          )
        the-view-box.the-view-box(
          v-if="statisticsIsOpen  || testIsOpen"
          :el-data="statisticsElSelected.viewBox"
          )
        section.network_info-section.the-network-field
          .info-section_head(
            v-if="statisticsIsOpen || testIsOpen"
            )
            h3 Map
          .info-section_main.js-info-section_main(
            @wheel.ctrl="scaleScroll($event)"
            )
            network-field(
              ref="networkField"
              :key="i"
              :style="{zoom: scaleNet + '%'}"
            )

        general-settings(v-if="showGlobalSet")
        general-result(v-if="showGlobalResult")
        select-core-side(v-if="showCoreSide")


    .workspace_meta
      include ./meta/workspace-meta.pug

</template>

<script src="./the-workspace.js"></script>

<style lang="scss" scoped>
  @import "../../scss/base";
  @import "./tabset/workspace-tabset";
  @import "./meta/workspace-meta";

  .page_workspace {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .workspace_tabset {
    flex: 0 0 auto;
    padding-top: 1px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  .workspace_content {
    display: flex;
    flex: 1 1 100%;
    overflow: hidden;
  }
  .network {
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
    &.open-test {
      grid-template-rows: auto 1fr 1fr;
      grid-template-columns: 1fr 1fr;
      grid-template-areas:  'the-testing   the-testing'
                            'view-box   the-statistics'
                            'network-field  network-field';

    }
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
  }
  .network_info-section {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .info-section_main {
    overflow: auto;
  }
  .workspace_meta {
    flex: 0 0 auto;
    background-color: $bg-workspace-2;
    display: flex;
    justify-content: space-between;
    padding: .5rem;
  }
  .workspace-relative {
    position: relative;
  }
</style>

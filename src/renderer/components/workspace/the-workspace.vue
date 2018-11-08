<template lang="pug">
  main.page_workspace
    .workspace_tabset
      include ./tabset/workspace-tabset.pug
    .workspace
      .workspace_content
        .network(
          v-if="currentNetwork === i"
          v-for="(net, i) in workspace"
          :key="net.i"
          :class="{'open-statistic': showStatistics !== 'close'}"
        )

          the-statistics(
            v-if="showStatistics === 'open'"
            :elData="selectedEl"
            )
          the-view-box(
            v-if="showStatistics === 'open'"
            :elData="selectedEl"
            )
          section.network_info-section
            .info-section_head(v-if="showStatistics === 'open'")
              h3 Map
            .info-section_main
              network-field(
              :netIndex="i"
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
  .workspace {
    display: flex;
    flex-direction: column;
    flex: 1 1 100%;
  }
  .workspace_tabset {
    padding-top: 1px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    //height: $h-sidebar-layers-item;
  }
  .workspace_content {
    background-color: $bg-workspace;
    display: flex;
    flex: 1 1 100%;
  }
  .network {
    display: flex;
    //flex-direction: row-reverse;
    flex: 1 1 100%;
    flex-wrap: wrap;
    width: 100%;
    &.open-statistic {
      .network_info-section {
        flex: 1 1 50%;
        height: 50%;
        overflow: hidden;
        &:first-child {
          flex: 0 0 100%;
        }
        &:nth-child(2n) {
          order: 1;
        }
      }
    }
  }
  .network_info-section {
    display: flex;
    flex-direction: column;
    flex: 1;
  }
  /*canvas {*/
    /*position: absolute;*/
    /*left: 0;*/
    /*right: 0;*/
    /*bottom: 0;*/
    /*top: 0;*/
    /*background-color: #040;*/
    /*width: 100%;*/
    /*height: 100%;*/
  /*}*/
  .workspace_meta {
    flex: 0 0 auto;
    background-color: $bg-workspace-2;
    display: flex;
    justify-content: space-between;
    padding: .5rem;
  }

</style>

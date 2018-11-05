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
          :class="{'open-statistic': showStatistics}"
        )
          section.network_info-section(v-if="showStatistics")
            .info-section
              .info-section_head
                .info-section_title
                  h3 Statistics
                .info-section_meta
                  button.btn.btn--link(type="button")
                    i.icon.icon-full-screen-graph
              .info-section_main
                chart-heatmap(:chartData="optionHeat")
                //ul.info-section_tab-set
                  li
                    button.btn(type="button")
                //.info-section_tab-set(v-if="true")
                  //chart-3d(:chartData="option3d")

                //.info-section_tab-set(v-if="true")
                //.info-section_tab-set(v-if="true")
                //.info-section_tab-set(v-if="true")
                //.info-section_tab-set(v-if="true")
                //.info-section_tab-set(v-if="true")


          section.network_info-section(v-if="showStatistics")
            .info-section
              .info-section_head
                .info-section_title
                  h3 Prediction vs Ground truth
                .info-section_meta
                  button.btn.btn--link(type="button")
                    i.icon.icon-full-screen-graph
              .info-section_main
                chart-bar(:chartData="optionBar")
            .info-section
              .info-section_head
                .info-section_title
                  h3 Batch Average Ground Truth vs Prediction
                .info-section_meta
                  button.btn.btn--link(type="button")
                    i.icon.icon-full-screen-graph
              .info-section_main
                chart-line(:chartData="optionLine")
          section.network_info-section
            .info-section
              .info-section_head(v-if="showStatistics")
                .info-section_title
                  h3 Map
                .info-section_meta
                  button.btn.btn--link(type="button")
                    i.icon.icon-full-screen-graph
              .info-section_main
                network-field(
                  :netIndex="i"
                  )
          section.network_info-section(v-if="showStatistics")
            .info-section
              .info-section_head
                .info-section_title
                  h3 ViewBox
                .info-section_meta
                  button.btn.btn--link(type="button")
                    i.icon.icon-full-screen-graph
              .info-section_main
                chart-3d(:chartData="option3d")

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
    flex: 1 1 100%;
    flex-wrap: wrap;
    &.open-statistic {
      .network_info-section {
        flex: 0 0 50%;
        height: 50%;
      }
    }
  }
  .network_info-section {
    display: flex;
    flex-direction: column;
    flex: 1;
    &:nth-child(2n) {
      border-left: 2px solid $bg-toolbar;;
    }
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
  .info-section {
    width: 100%;
    flex: 1 1 50%;
    display: flex;
    flex-direction: column;
  }
  .info-section_head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: $bg-toolbar;
    padding: .7rem 1rem;
    flex: 0 0 auto;
  }
  .info-section_title {
    h3 {
      margin: 0;
    }
  }
  .info-section_meta {}
  .info-section_main {
    flex: 1 1 100%;
    display: flex;
  }
  .info-section_tab-set {
    flex: 1 1 100%;
    display: flex;
  }
</style>

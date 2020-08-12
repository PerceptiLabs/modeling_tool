<template lang="pug">
  div.wrapper
    //- router-link.nav-link(
    //-   :to="{name: 'app'}")
    //-   svg(xmlns='http://www.w3.org/2000/svg' width='18' height='20' viewbox='0 0 18 20' fill='none')
    //-     path(d='M8.84619 0L0 5.01709V8.90789L8.84619 13.925L17.6924 8.90789V5.01709L8.84619 0ZM14.1192 6.89423L8.84619 9.89766L3.57317 6.89423L8.84619 3.8908L14.1192 6.89423Z' fill='#C4C4C4')
    //-     path(d='M0 11.092V14.9828L8.84619 19.9999L17.6924 14.9828V11.092L8.84619 16.1433L0 11.092Z' fill='#C4C4C4')
    router-link.nav-link(
      :class="{'is-active': this.$route.name === 'projects'}"
      :to="{name: 'projects'}"
      v-tooltip:right="'ModelHub'"
      )
      svg(xmlns='http://www.w3.org/2000/svg' width='21' height='12' viewbox='0 0 21 12' fill='none')
        path(fill-rule='evenodd' clip-rule='evenodd' d='M9.04773 0H19.0478C19.6001 0 20.0478 0.447715 20.0478 1V3.79031C20.0478 4.3426 19.6001 4.79031 19.0478 4.79031H9.04773C8.49544 4.79031 8.04773 4.3426 8.04773 3.79031V3.61304H3.73244C3.38663 4.21084 2.74028 4.61304 2 4.61304C0.89543 4.61304 0 3.71761 0 2.61304C0 1.50847 0.89543 0.613037 2 0.613037C2.74028 0.613037 3.38663 1.01524 3.73244 1.61304H8.04773V1C8.04773 0.447715 8.49544 0 9.04773 0ZM3.73244 10.613H8H8.04773V10.976C8.04773 11.5283 8.49544 11.976 9.04773 11.976H19.0478C19.6001 11.976 20.0478 11.5283 20.0478 10.976V8.18567C20.0478 7.63338 19.6001 7.18567 19.0478 7.18567H9.04773C8.49544 7.18567 8.04773 7.63338 8.04773 8.18567V8.61304H8H3.73244C3.38663 8.01524 2.74028 7.61304 2 7.61304C0.89543 7.61304 0 8.50847 0 9.61304C0 10.7176 0.89543 11.613 2 11.613C2.74028 11.613 3.38663 11.2108 3.73244 10.613Z' fill='#C4C4C4')
    div.nav-link(
      :class="{'is-active': isOnModelToolPage() && !statisticsIsOpen && !isStatistiOrTestOpened , 'disabled': !networkIsNotEmpty}"
      @click="toModelingTool()"
      v-tooltip:right="'Modeling Tool'"
      )
      svg(xmlns='http://www.w3.org/2000/svg' width='20' height='21' viewbox='0 0 20 21' fill='none')
        path(d='M20 7.65595V13.2904C20 13.8065 19.5699 14.2366 19.0538 14.2366H13.4194C12.9033 14.1936 12.4731 13.7635 12.4731 13.2473V7.65595C12.4731 7.13982 12.9033 6.70972 13.4194 6.70972H19.0538C19.5699 6.70972 20 7.13982 20 7.65595Z' fill='#C4C4C4')
        path(d='M4.68813 7.2688H2.79565V13.2903H4.68813V7.2688Z' fill='#C4C4C4')
        path(d='M16.258 2.79565H7.2688V4.51608C7.2688 4.5591 7.2688 4.64512 7.2688 4.68813H15.3118V10.4516C15.3118 10.9677 15.7419 11.3978 16.258 11.3978C16.7742 11.3978 17.2043 10.9677 17.2043 10.4516V3.74189C17.1613 3.22576 16.7742 2.79565 16.258 2.79565Z' fill='#C4C4C4')
        path(d='M6.53763 7.44086H0.903226C0.387097 7.44086 0 7.05376 0 6.53763V0.903226C0 0.387097 0.387097 0 0.903226 0H6.53763C7.05376 0 7.44086 0.387097 7.44086 0.903226V6.53763C7.44086 7.05376 7.05376 7.44086 6.53763 7.44086ZM0.903226 0.860215C0.860215 0.860215 0.860215 0.860215 0.860215 0.903226V6.53763C0.860215 6.58065 0.860215 6.58065 0.903226 6.58065H6.53763C6.58065 6.58065 6.58065 6.58065 6.58065 6.53763V0.903226C6.58065 0.860215 6.58065 0.860215 6.53763 0.860215H0.903226Z' fill='#C4C4C4')
        path(d='M6.53763 20.5163H0.903226C0.387097 20.5163 0 20.1292 0 19.6131V13.9787C0 13.4625 0.387097 13.0754 0.903226 13.0754H6.53763C7.05376 13.0754 7.44086 13.4625 7.44086 13.9787V19.6131C7.44086 20.1292 7.05376 20.5163 6.53763 20.5163ZM0.903226 13.9357C0.860215 13.9357 0.860215 13.9357 0.860215 13.9787V19.6131C0.860215 19.6561 0.860215 19.6561 0.903226 19.6561H6.53763C6.58065 19.6561 6.58065 19.6561 6.58065 19.6131V13.9787C6.58065 13.9357 6.58065 13.9357 6.53763 13.9357H0.903226Z' fill='#C4C4C4')
    div.nav-link(:class="{'disabled': !haveAtLeastOneItemStatistic , 'is-active': statisticsIsOpen && isOnModelToolPage()}"
      @click="toModelStatistic()"
      v-tooltip:right="'Statistics View'"
      )
      svg(xmlns='http://www.w3.org/2000/svg' width='20' height='24' viewbox='0 0 20 24' fill='none')
        path(d='M12.1292 7.01069V9.37628C12.1292 9.89241 11.6991 10.3225 11.1829 10.3225H8.81733C8.3012 10.3225 7.87109 9.89241 7.87109 9.37628V7.01069C7.87109 6.49456 8.3012 6.06445 8.81733 6.06445H11.1829C11.6991 6.06445 12.1292 6.49456 12.1292 7.01069Z' fill='#C4C4C4')
        path(d='M3.6129 17.4623H1.76344C0.817204 17.4623 0 16.6881 0 15.6988V13.8494C0 12.8601 0.774194 12.0859 1.76344 12.0859H3.6129C4.60215 12.0859 5.37634 12.8601 5.37634 13.8494V15.6988C5.33333 16.6881 4.55914 17.4623 3.6129 17.4623ZM1.76344 13.2472C1.41935 13.2472 1.11828 13.5483 1.11828 13.8924V15.7419C1.11828 16.0859 1.41935 16.387 1.76344 16.387H3.6129C3.95699 16.387 4.25806 16.0859 4.25806 15.7419V13.8924C4.25806 13.5483 3.95699 13.2472 3.6129 13.2472H1.76344Z' fill='#C4C4C4')
        path(d='M19.4409 7.01069V9.37628C19.4409 9.89241 19.0108 10.3225 18.4947 10.3225H16.1291C15.613 10.3225 15.1829 9.89241 15.1829 9.37628V7.01069C15.1829 6.49456 15.613 6.06445 16.1291 6.06445H18.4947C19.0108 6.06445 19.4409 6.49456 19.4409 7.01069Z' fill='#C4C4C4')
        path(d='M19.4409 0.946237V3.31183C19.4409 3.82796 19.0108 4.25806 18.4947 4.25806H16.1291C15.613 4.25806 15.1829 3.82796 15.1829 3.31183V0.946237C15.1829 0.430108 15.613 0 16.1291 0H18.4947C19.0108 0 19.4409 0.430108 19.4409 0.946237Z' fill='#C4C4C4')
        path(d='M10.8817 20.473H9.03224C8.04299 20.473 7.2688 19.6988 7.2688 18.7096V13.8923C7.2688 12.9031 8.04299 12.1289 9.03224 12.1289H10.8817C11.8709 12.1289 12.6451 12.9031 12.6451 13.8923V18.7096C12.6451 19.6988 11.8709 20.473 10.8817 20.473ZM9.07525 13.2472C8.73116 13.2472 8.43009 13.5483 8.43009 13.8923V18.7096C8.43009 19.0536 8.73116 19.3547 9.07525 19.3547H10.9247C11.2688 19.3547 11.5699 19.0536 11.5699 18.7096V13.8923C11.5699 13.5483 11.2688 13.2472 10.9247 13.2472H9.07525Z' fill='#C4C4C4')
        path(d='M18.2366 23.7418H16.3871C15.4409 23.7418 14.6237 22.9676 14.6237 21.9784V13.8923C14.6237 12.9031 15.3979 12.1289 16.3871 12.1289H18.2366C19.2258 12.1289 20 12.9031 20 13.8923V21.9784C20 22.9246 19.2258 23.7418 18.2366 23.7418ZM16.3871 13.2472C16.043 13.2472 15.7419 13.5483 15.7419 13.8923V21.9784C15.7419 22.3225 16.043 22.6235 16.3871 22.6235H18.2366C18.5806 22.6235 18.8817 22.3225 18.8817 21.9784V13.8923C18.8817 13.5483 18.5806 13.2472 18.2366 13.2472H16.3871Z' fill='#C4C4C4')
    div.nav-link(:class="{'disabled': !haveAtLeastOneTestItem , 'is-active-stroke': testIsOpen && isOnModelToolPage()}"
      @click="toModelTest()"
      v-tooltip:right="'Test View'"
      )
      svg(xmlns="http://www.w3.org/2000/svg" width="42" height="42" viewBox="0 0 42 42" fill="none")
        path(class="test-borders" d="M24.1 11H17.9C17.6239 11 17.4 11.2239 17.4 11.5V12.2273C17.4 12.5034 17.6239 12.7273 17.9 12.7273H18.1C18.2105 12.7273 18.3 12.8159 18.3 12.9263C18.2991 14.4189 18.2801 17.1218 17.85 18.7727C17.5185 20.0453 15.3144 23.9741 13.577 27.1057C12.8486 28.4186 13.7959 30 15.2973 30H26.7748C28.2589 30 29.2003 28.454 28.4838 27.1543C26.7375 23.9865 24.4854 20.0602 24.15 18.7727C23.7184 17.1159 23.7007 14.532 23.7 12.9266C23.7 12.8162 23.7895 12.7273 23.9 12.7273H24.1C24.3761 12.7273 24.6 12.5034 24.6 12.2273V11.5C24.6 11.2239 24.3761 11 24.1 11Z" stroke="#C4C4C4")
        path( class="test-borders" d="M17 21H25" stroke="#C4C4C4" stroke-width="2")
        g(clip-path="url(#clip0)")
          path(class="test-fill test-borders" d="M24.1 11H17.9C17.6239 11 17.4 11.2239 17.4 11.5V12.2273C17.4 12.5034 17.6239 12.7273 17.9 12.7273H18.1C18.2105 12.7273 18.3 12.8159 18.3 12.9263C18.2991 14.4189 18.2801 17.1218 17.85 18.7727C17.5185 20.0453 15.3144 23.9741 13.577 27.1057C12.8486 28.4186 13.7959 30 15.2973 30H26.7748C28.2589 30 29.2003 28.454 28.4838 27.1543C26.7375 23.9865 24.4854 20.0602 24.15 18.7727C23.7184 17.1159 23.7007 14.532 23.7 12.9266C23.7 12.8162 23.7895 12.7273 23.9 12.7273H24.1C24.3761 12.7273 24.6 12.5034 24.6 12.2273V11.5C24.6 11.2239 24.3761 11 24.1 11Z" fill="#C4C4C4" stroke="#C4C4C4")
        
        defs
          clipPath(id="clip0")
            rect(width="18" height="10" fill="white" transform="translate(12 21)")

    router-link.nav-link(
      :class="{'is-active': this.$route.name === 'settings'}"
      :to="{name: 'settings'}"
      v-tooltip:right="'Settings'"
      )
      svg(xmlns='http://www.w3.org/2000/svg' width='19' height='20' viewbox='0 0 19 20' fill='none')
        path(d='M16.4657 10.3828C16.4657 10.0828 16.5657 9.78284 16.5657 9.48284C16.5657 9.18284 16.5657 8.88284 16.4657 8.58284L18.4657 6.98284C18.6657 6.88284 18.6657 6.58284 18.5657 6.38284L16.6657 3.08284C16.5657 2.88284 16.2657 2.78284 16.0657 2.88284L13.6657 3.88284C13.1657 3.48284 12.6657 3.18284 12.0657 2.98284L11.6657 0.482843C11.6657 0.282843 11.4657 0.0828427 11.1657 0.0828427H7.36569C7.16569 -0.117157 6.96569 0.0828427 6.86569 0.282843L6.56569 2.88284C5.96569 3.08284 5.46569 3.38284 4.96569 3.78284L2.56569 2.78284C2.36569 2.78284 2.06569 2.78284 1.96569 2.98284L0.0656854 6.38284C-0.0343146 6.58284 -0.0343146 6.78284 0.165685 6.98284L2.16569 8.58284C2.16569 8.88284 2.06569 9.18284 2.06569 9.48284C2.06569 9.78284 2.06569 10.0828 2.16569 10.3828L0.165685 11.9828C-0.0343146 12.0828 -0.0343146 12.3828 0.0656854 12.5828L1.96569 15.8828C2.06569 16.0828 2.36569 16.1828 2.56569 16.0828L4.96569 15.0828C5.46569 15.4828 5.96569 15.7828 6.56569 15.9828L6.96569 18.4828C6.96569 18.8828 7.16569 19.0828 7.36569 19.0828H11.1657C11.3657 19.0828 11.5657 18.8828 11.6657 18.6828L12.0657 16.1828C12.6657 15.9828 13.1657 15.5828 13.6657 15.2828L16.0657 16.2828C16.2657 16.3828 16.5657 16.2828 16.6657 16.0828L18.5657 12.7828C18.6657 12.5828 18.6657 12.2828 18.4657 12.1828L16.4657 10.3828ZM9.26569 13.0828C7.26569 13.0828 5.66569 11.4828 5.66569 9.48284C5.66569 7.48284 7.36569 5.88284 9.26569 5.88284C11.1657 5.88284 12.8657 7.48284 12.8657 9.48284C12.8657 11.4828 11.2657 13.0828 9.26569 13.0828Z' fill='#C4C4C4')

</template>

<script>
  import { mapState, mapActions, mapGetters }  from 'vuex';
  export default {
    name: 'ProjectSidebar',
    data() {
      return {
        haveAtLeastOneItemStatistic: false,
        statisticItemIndex: null,

        haveAtLeastOneTestItem: false,
        testItemIndex: null,
      }
    },
    created(){
      this.handleStatisticState(this.workspaceModels);
      this.handleTestState(this.workspaceModels);
    },
    computed: {
      ...mapState({
        workspaceModels: state => state.mod_workspace.workspaceContent,
      }),
      ...mapGetters({
        statisticsIsOpen:   'mod_workspace/GET_statisticsIsOpen',
        testIsOpen:         'mod_workspace/GET_testIsOpen',
        currnetNetwork:     'mod_workspace/GET_currentNetwork',
        networkIsNotEmpty:  'mod_workspace/GET_networkIsNotEmpty',
      }),
      isStatistiOrTestOpened() {
        const currentItemNetwork = this.$store.getters['mod_workspace/GET_currentNetwork'];
        if(!currentItemNetwork.hasOwnProperty('networkMeta')) return false;
        return currentItemNetwork.networkMeta.openStatistics === true || currentItemNetwork.networkMeta.openTest === true;
     },
      
    },
    watch: {
      workspaceModels: {
        deep: true,
        handler(models) {
          this.resetModelIndexes();
          this.handelModelIndexes(models);
        }
      },
    },
    methods: {
      ...mapActions({
        SET_currentNetwork: 'mod_workspace/SET_currentNetwork',
        SET_openStatistics: 'mod_workspace/SET_openStatistics',
        SET_openTest: 'mod_workspace/SET_openTest',
        set_chartRequests:    'mod_workspace/SET_chartsRequestsIfNeeded',
      }),
      resetModelIndexes() {
        this.reseStatistic();
        this.resetTest();
      },
      reseStatistic(){
        this.statisticItemIndex = null;
        this.haveAtLeastOneItemStatistic = false;
      },
      resetTest() {
        this.testItemIndex = null;
        this.haveAtLeastOneTestItem = false;
      },
      handelModelIndexes(models){
        this.handleStatisticState(models);
        this.handleTestState(models);
      },
      handleStatisticState(models) {
        const firsImteWithStatistcsIndex = models.findIndex(model => model.networkMeta.openStatistics !== null);
        if(firsImteWithStatistcsIndex !== -1) {
           this.haveAtLeastOneItemStatistic = true;
           this.statisticItemIndex = firsImteWithStatistcsIndex;
        } else {
          this.haveAtLeastOneItemStatistic = false;
          this.statisticItemIndex = null;
        }
      },
      handleTestState(models) {
        const firstItemWithTextIndex = models.findIndex(model => model.networkMeta.openTest !== null && model.networkMeta.coreStatus.Status === 'Finished');
        
        if(firstItemWithTextIndex !== -1) {
          this.haveAtLeastOneTestItem = true;
          this.testItemIndex = firstItemWithTextIndex;
        } else {
          this.haveAtLeastOneTestItem = false;
          this.testItemIndex = null;
        }

      },
      isOnModelToolPage(){
        return this.$route.name === 'app';
      },
      doesCurrentNetworkHaveTest() {
        return this.currnetNetwork.networkMeta.openTest !== null &&  this.currnetNetwork.networkMeta.coreStatus.Status === 'Finished'
      },
      isModelPageAndNetworkHasStatistic() {
        return this.$route.name === 'app' && this.currnetNetwork.networkMeta.openStatistics !== null
      },
      isModelPageAndNetworkHasStatistic() {
        return this.$route.name === 'app' && this.currnetNetwork.networkMeta.openStatistics !== null
      },
      toModelStatistic() {
        //$route.name === 'app' && currnetNetwork.networkMeta.openStatistics !== null
        if(this.$route.name === 'app') {
          // networkMeta.openStatistics !== null
          if(this.isModelPageAndNetworkHasStatistic()) {
            this.$store.commit("mod_workspace/setViewType", 'statistic');
            const item = this.workspaceModels[this.statisticItemIndex];
            this.SET_currentNetwork(this.statisticItemIndex)
              .then(() => { 
                this.$store.dispatch("mod_workspace/EVENT_onceDoRequest");
                this.SET_openStatistics(true);
                this.set_chartRequests(item.networkID);
                })

          } else {
            const { statisticItemIndex } = this;
            
            if(statisticItemIndex !== null) {
              this.$store.commit("mod_workspace/setViewType", 'statistic');
              this.SET_currentNetwork(statisticItemIndex);
              this.SET_openStatistics(true);
              this.SET_openTest(false);
            }
          }



        } else {
          const { statisticItemIndex } = this;
          if(statisticItemIndex !== null) {
            this.$store.commit("mod_workspace/setViewType", 'statistic');
            this.SET_currentNetwork(statisticItemIndex)
              .then(() => {
                this.$router.push({name: 'app'});
                this.SET_openStatistics(true);
              });
            
          }
        }
      },
      isOnStatisticsView() {
        return this.currnetNetwork.networkMeta.openStatistics === true
      },
      isOnTestView() {
        return this.currnetNetwork.networkMeta.openTest === true
      },
      haveCurrentModelStatistics() {
        return this.currnetNetwork.networkMeta.openStatistics !== null
      },
      haveCurrentModelTest() {
        return this.currnetNetwork.networkMeta.openTest !== null
      },
      isOnModelingToolPage() {
        return this.$route.name === 'app';
      },
      toModelingTool() {
        if(this.isOnModelingToolPage()) {
          this.$store.commit("mod_workspace/setViewType", 'model');
          if (this.isOnStatisticsView()) {
            this.SET_openStatistics(false);
          } else if (this.isOnTestView()) {
            this.SET_openTest(false);
          }
        } else {
          this.$store.commit("mod_workspace/setViewType", 'model');
          this.SET_currentNetwork(0);
          if (this.isOnStatisticsView()) {
            this.SET_openStatistics(false);
          } else if (this.isOnTestView()) {
            this.SET_openTest(false);
          }
          this.$router.push({name: 'app'});
        }
      },
      toModelTest() {
        if(this.haveAtLeastOneTestItem) {
          this.$store.commit("mod_workspace/setViewType", 'test');

          if(this.isOnModelToolPage()) {
            if(this.doesCurrentNetworkHaveTest()) {
              this.SET_openTest(true);
            } else {
              this.SET_currentNetwork(this.testItemIndex);
              this.SET_openTest(true);
            }
          } else {
            this.SET_currentNetwork(this.testItemIndex)
              .then(_ => {
                this.$router.push({name: 'app'});
                this.SET_openTest(true);
              });
          }
        }
      },
    },
  }
 
</script>

<style lang="scss" scoped>
  .wrapper {
    position: fixed;
    left: 0;
    width: 46px;
    height: 100vh;
    background: #23252A;
    // box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);
  }
  .logo-link {
    display: block;
    padding-top: 10px;
    margin-left: 1px;
    margin-bottom: 5px;
  }
  .nav-link {
    cursor: pointer;
    margin-top: 4px;
    position: relative;
    display: flex;
    height: 42px;
    width: 42px;
    justify-content: center;
    align-items: center;
    border: 1px solid rgba(97, 133, 238, 0.5);
    box-sizing: border-box;
    border-radius: 2px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;

    &.is-active-stroke {
      border-left-width:  5px;
      border-color: #6185EE;
      border-right-width: 0;
      width: 46px;
      .test-borders {
        stroke: #fff;
      }
      .test-fill {
        fill: #fff;
      }
    }
    &.is-active {
      border-left-width:  5px;
      border-color: #6185EE;
      border-right-width: 0;
      width: 46px;
      svg, path {
        fill: #fff;
      }
      // border-radius: 10px 0px 0px 10px;
      &:after {
        // content: '';
        // position: absolute;
        // left: 0;
        // top: 0;
        // background-color: #fff;
        // width: 2px;
        // height: 100%;
      }
    }
  }
  .disabled {
    cursor: default;
    opacity: 0.3;
}
</style>
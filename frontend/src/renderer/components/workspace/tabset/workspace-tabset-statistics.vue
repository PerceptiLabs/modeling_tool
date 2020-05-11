<template lang="pug">
  //- ul.statistics-box_tabset
  //-   li.statistics-box_tab(
  //-     v-for="(tabINfo, name, i) in tabSet"
  //-     :key="name"
  //-   )
  //-     button.btn.btn--tabs.statistics-box_btn.tutorial-relative(type="button"
  //-       v-if="tabINfo"
  //-       @click="setCurrentTab(name, tabINfo.btnId)"
  //-       v-tooltip-interactive:bottom="tabINfo.btnInteractiveInfo"
  //-       :class="[currentTab === name ?  'active' : '', tabINfo.btnClass]"
  //-       :id="tabINfo.btnId"
  //-     ) {{ name }}

  //-     button.btn.btn--tabs.statistics-box_btn(type="button"
  //-       v-else
  //-       @click="setCurrentTab(name)"
  //-       :class="{'active': currentTab === name}"
  //-     ) {{ name }}

  ul.bookmark_tab-list
    li.bookmark_tab.workspace_tab(
      v-for="(tabINfo, name, i) in tabSet"
      :key="name"
    )
      button.btn.btn--tabs.statistics-box_btn.tutorial-relative(type="button"
        v-if="tabINfo"
        @click="setCurrentTab(name, tabINfo.btnId)"
        v-tooltip-interactive:bottom="tabINfo.btnInteractiveInfo"
        :class="[currentTab === name ?  'active' : '', tabINfo.btnClass]"
        :id="tabINfo.btnId"
      ) {{ name }}

      button.btn.btn--tabs.statistics-box_btn(type="button"
        v-else
        @click="setCurrentTab(name)"
        :class="{'active': currentTab === name}"
      ) {{ name }}
</template>

<script>
import {mapActions, mapGetters, mapMutations, mapState} from 'vuex';

export default {
  data() {
    return {
      tabSet: []
    }
  },
  computed: {
    ...mapState({
      statisticsElSelected:       state => state.mod_statistics.selectedElArr,
    }),
  },
}
</script>

<style lang="scss">
@import "../../../scss/base";

</style>

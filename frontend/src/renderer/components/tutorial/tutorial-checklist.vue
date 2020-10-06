<template lang="pug">
#tutorial-checklist(v-if="isTutorialMode")
  .checklist-header(@click="toggleChecklist")
    span Get started checklist
    svg(v-if="isChecklistExpanded" width="12" height="7" viewBox="0 0 12 7" fill="none" xmlns="http://www.w3.org/2000/svg")
      path(fill-rule="evenodd" clip-rule="evenodd" d="M0.437065 1.3112C0.195681 1.06981 0.195681 0.67845 0.437065 0.437065C0.67845 0.195681 1.06981 0.195681 1.3112 0.437065L5.29289 4.41876C5.68342 4.80929 6.31658 4.80929 6.70711 4.41876L10.6888 0.437065C10.9302 0.195681 11.3215 0.195681 11.5629 0.437065C11.8043 0.67845 11.8043 1.06981 11.5629 1.3112L6.70711 6.16702C6.31658 6.55755 5.68342 6.55755 5.29289 6.16702L0.437065 1.3112Z" fill="#C4C4C4")
    svg(v-else width="12" height="7" viewBox="0 0 12 7" fill="none" xmlns="http://www.w3.org/2000/svg")
      path(fill-rule="evenodd" clip-rule="evenodd" d="M11.5629 5.5638C11.8043 5.80519 11.8043 6.19655 11.5629 6.43793C11.3216 6.67932 10.9302 6.67932 10.6888 6.43793L6.70711 2.45624C6.31658 2.06571 5.68342 2.06571 5.29289 2.45624L1.3112 6.43793C1.06981 6.67932 0.678451 6.67932 0.437066 6.43793C0.195681 6.19655 0.195681 5.80519 0.437066 5.5638L5.29289 0.707977C5.68342 0.317453 6.31658 0.317452 6.70711 0.707977L11.5629 5.5638Z" fill="#C4C4C4")

  .checklist-content(v-if="isChecklistExpanded")

    .checklist-content-section
      .checklist-content-item.watch-tutorial(@click="openVideoTutorials")
        .item-icon
          svg(width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M7.5 15C11.6421 15 15 11.6421 15 7.5C15 3.35786 11.6421 0 7.5 0C3.35786 0 0 3.35786 0 7.5C0 11.6421 3.35786 15 7.5 15ZM11 7.11111L5 4V11L11 7.11111Z" fill="#B6C7FB")
      
        span.item-label Watch a demo

    .checklist-section-separator

    .checklist-content-section
      .checklist-content-item(v-for="i in checklistItems"
        :key="i.label")
        .item-icon
          svg(v-if="i.isCompleted" width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(d="M3 7.38624L5.76923 11.1111L11 4" stroke="#73FEBB" stroke-linecap="round" stroke-linejoin="round")
            circle(cx="7.5" cy="7.5" r="7" stroke="#73FEBB")
          svg(v-else width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg")
            circle(cx="7.5" cy="7.5" r="7" stroke="#B6C7FB")

        span.item-label(:class="{'is-completed': i.isCompleted}") {{ i.label }}

    .checklist-content-section.checklist-skip
      span(@click.stop="skipChecklist") Skip
</template>

<script>
import { mapGetters, mapMutations, mapActions } from 'vuex';
export default {
  name: 'TutorialChecklist',
  data() {
    return {
    }
  },
  computed: {
    ...mapGetters({
      isTutorialMode:             'mod_tutorials/getIsTutorialMode',
      isChecklistExpanded:        'mod_tutorials/getIsChecklistExpanded',
      checklistItems:             'mod_tutorials/getChecklistItems'
    }),
  },
  methods: {
    ...mapMutations({
      setChecklistExpandedState:  'mod_tutorials/setChecklistExpandedState'
    }),
    ...mapActions({
      setShowChecklist:           'mod_tutorials/setShowChecklist',
      trackSkipChecklist:         'mod_tracker/EVENT_skipChecklist',

    }),
    toggleChecklist() {
      this.setChecklistExpandedState(!this.isChecklistExpanded);
    },
    openVideoTutorials() {
      window.open('https://www.youtube.com/watch?v=tdELIpi-BZI', '_blank');
    },
    skipChecklist() {
      this.trackSkipChecklist();
      this.setShowChecklist(false);
    }
  }
}

</script>
<style lang="scss" scoped>
// @import "../../scss/base";
// @import "../../scss/directives/tooltip";

$medium-separation: 1.8rem;
$small-separation: 1.5rem;

* {
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 600;
  font-size: 14px;
  line-height: 18px;

  box-sizing: border-box;
}

#tutorial-checklist {
  transition:all 200ms ease;

  position: fixed;
  right: 0;
  bottom: 0;

  width: 20rem;

  z-index: 100;
}

.checklist-header {
  height: 3.5rem;
  
  display: flex;
  justify-content: space-around;
  align-items: center;

  background: #6185EE;

  border-radius: 2px 2px 0px 0px;  
}

.checklist-content {
  background: url('../../../../static/img/tutorial/tutorial-background.png');
  background-size: cover; 
}

.checklist-content-section {

  margin-left: $medium-separation;
  margin-right: $medium-separation;

  &:first-of-type {
    padding-top: $medium-separation;
  }

  &:last-of-type {
    padding-bottom: $medium-separation;
  }

  // + .checklist-content-section {
  //   margin-top: $medium-separation;
  // }
}

.checklist-section-separator {
  width: 18rem;
  height: 1px;

  margin: $medium-separation auto;

  background: #363E51;
}

.checklist-content-item {
  min-height: $small-separation;

  display: flex;
  align-items: flex-start;

  &.watch-tutorial {
    cursor: pointer;
  }

  + .checklist-content-item {
    margin-top: $small-separation;
  }

  > .item-icon + span {
    display: inline-block;
    margin-left: 1rem;
  }

  .item-label.is-completed {
    text-decoration: line-through;
    color: #818181;
  }
}

.checklist-skip {
  margin-top: 2rem;

  > span {
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: normal;
    font-size: 11px;
    line-height: 18px;
    color: #818181;
    text-decoration: underline;

    cursor: pointer;
  }
}

</style>

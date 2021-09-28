<template lang="pug">
  div.components-settings-lock-wrapper(
    :class="{'is-locked': selectedEl && selectedEl.isSettingsLocked }"
  )
    .components-settings-lock-content(v-if="selectedEl && selectedEl.isSettingsLocked ")
      img.components-settings-lock-content-icon(src="../../../../static/img/lock.svg")
      p.components-settings-lock-content-text Reset to standard <br/> settings to unlock
    slot
</template>
<script>
export default {
  name: 'SidebarLockedSettingsWrapper',
  props: {
    selectedEl: {
      default: function() { return {}}
    }
  }
}
</script>

<style lang="scss" scoped>
  .components-settings-lock-wrapper {
    min-height: calc(100% - 30px);
    position: relative;
    &.is-locked {
      &:after {
        content: '';
        position: absolute;
        z-index: 1;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        background: theme-var($neutral-7);
        opacity: 0.9;
        backdrop-filter: blur(4px);
      }
    }
  }
  .components-settings-lock-content {
    position: absolute;
    z-index: 2;
    left: 0;
    top: 0;
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  .components-settings-lock-content-icon {
    margin-bottom: 10px;
  }
  .components-settings-lock-content-text {
    font-family: Nunito Sans;
    font-size: 12px;
    font-style: normal;
    font-weight: 400;
    line-height: 15px;
    letter-spacing: 0em;
    text-align: center;
    color: #B6C7FB;
    opacity: 0.75;
      
  }
</style>
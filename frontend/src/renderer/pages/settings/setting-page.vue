<template lang="pug">
  div
    .setting-page
      .setting-tabs-wrapper
        ul.tab-list
          li.tab-item.active Profile
          //- li.tab-item.tab-item-disabled Account
          //- li.tab-item.tab-item-disabled Teams
      .setting-content
        setting-profile
        
</template>
<script>
  import SettingProfile     from '@/pages/settings/setting-profile.vue'; 
export default {
  name: 'SettingPage',
  components: { SettingProfile }
}
</script>
<style lang="scss" scoped>
.setting-page {
  margin-top: 5px;
  margin-right: 5px;
  background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
  border: 1px solid rgba(97, 133, 238, 0.4);
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
  min-height: calc(100vh - 50px);
}
.setting-tabs-wrapper {
  margin: 30px 15px 45px;
}
.tab-list {
  border-bottom: 1px solid #4D556A;
}
.tab-item {
  display: inline-block;
  position: relative;
  cursor: pointer;
  margin-left: 30px;
  font-family: Nunito Sans;
  font-size: 16px;
  line-height: 22px;
  margin-bottom: 10px;
  color: #818181;
  &.active {
    color: #9BB2F6;
    font-weight: bold;
    &:after {
      content: '';
      position: absolute;
      left: 0;
      bottom: -12px;
      width: 100%;
      height: 3px;
      background: #9BB2F6;
      border-radius: 10px;
    }
  }
}
.tab-item-disabled {
  cursor: default;
}
.setting-content {
  margin-left: 45px;
  margin-right: 45px;
}
</style>
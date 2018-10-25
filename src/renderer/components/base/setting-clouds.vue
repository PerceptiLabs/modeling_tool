<template lang="pug">
  .clouds-component
    ul.clouds-component_head
      li(
        v-for="(cloud, i) in cloudsList"
        :key="i"
        )
        button.btn.cloud_btn(
          type="button"
          :class="{'active': selectedCloud == i}"
          @click="setCloud(i)"
          )
          i.icon(:class="cloud")
    .clouds-component_body(v-if="selectedCloud == 0")
      .popup_line
      ul.cloud_account-list
        li
          base-radio(groupName="cloud")
            i.icon.icon-cloud
            span  Account: Quantum net
          button.btn.btn--link(type="button") Log out
        li
          base-radio(groupName="cloud")
            i.icon.icon-cloud
            span  Account: Quantum net
          button.btn.btn--link(type="button") Log out
        li
          button.btn.btn--link.cloud_account-add-btn(type="button")
            i.icon.icon-cloud
            span  Add account
      .popup_line
      .form_row
        input.form_input(type="text" placeholder="Link")
        button.btn.btn--primary(type="button") Load
    .clouds-component_body(v-if="selectedCloud == 1")
      .popup_line
      .form_table
        .form_row
          label.form_label Username
          input.form_input(type="text")
        .form_row
          label.form_label Password
          input.form_input(type="password")
      .popup_foot
        button.btn.btn--primary(type="button") Log in
    .clouds-component_body(v-if="selectedCloud == 2")
    .clouds-component_body(v-if="selectedCloud == 3")
    .clouds-component_body(v-if="selectedCloud == 4")


</template>

<script>
export default {
  name: "SettingsCloud",
  data() {
    return {
      selectedCloud: null,
      cloudsList: ['icon-cloud', 'icon-dropbox-logo', 'icon-g-drive', 'icon-onedrive', 'icon-cloud-add']
    }
  },
  methods: {
    setCloud(i) {
      this.selectedCloud = i;
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  //.clouds-component
  .clouds-component_head {
    display: flex;
    justify-content: space-between;
  }
  .cloud_btn {
    transition: none;
    color: $bg-input;
    border: 2px solid;
    width: 4.6rem;
    height: 4.6rem;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
    font-size: 2rem;
    &:hover,
    &.active {
      box-shadow: $icon-shad;
    }
    &.active {
      color: $col-txt;
      border: none;
      background: $bg-grad-blue;
    }
  }
  .clouds-component_body {
    padding-top: 2rem;
    .popup_line {
      margin-bottom: 1rem;
    }
  }
  .cloud_account-list {
    margin-bottom: 1rem;
    li {
      padding: .25em 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
  }
  .cloud_account-add-btn {
    margin-left: 1.4em;
    &:hover {
      color: $col-warning;
    }
  }
</style>

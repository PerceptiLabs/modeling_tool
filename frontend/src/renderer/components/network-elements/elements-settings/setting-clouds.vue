<template lang="pug">
.settings-layer
  .settings-layer_section
    ul.clouds-component_head
      li(v-for="(cloud, i) in cloudsList", :key="i")
        button.btn.cloud_btn(
          type="button",
          :class="{ active: selectedCloud == i }",
          @click="setCloud(i)"
        )
          i.icon(:class="cloud")
  .clouds-component_body.settings-layer_section(v-if="selectedCloud == 0")
    ul.cloud_account-list
      li
        base-radio(group-name="cloud")
          i.icon.icon-cloud
          span Account: PerceptiLabs net
        button.btn.btn--link(type="button") Log out
      li
        base-radio(group-name="cloud")
          i.icon.icon-cloud
          span Account: PerceptiLabs net
        button.btn.btn--link(type="button") Log out
      li
        button.btn.btn--link.cloud_account-add-btn(type="button")
          i.icon.icon-cloud
          span Add account
    .form_row
      input.form_input(type="text", placeholder="Link")
      button.btn.btn--primary(type="button") Load
  .clouds-component_body.settings-layer_section(v-if="selectedCloud == 1")
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
      cloudsList: [
        "icon-cloud",
        "icon-dropbox-logo",
        "icon-g-drive",
        "icon-onedrive",
        "icon-cloud-add"
      ]
    };
  },
  methods: {
    setCloud(i) {
      this.selectedCloud = i;
    }
  }
};
</script>

<style lang="scss" scoped>
.clouds-component_head {
  display: flex;
  justify-content: space-between;
}
.cloud_btn {
  font-size: 2rem;
  line-height: 1;
  color: $bg-input;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 4.6rem;
  height: 4.6rem;
  transition: none;
  border: 2px solid;
  &:hover,
  &.active {
    box-shadow: $icon-shad;
  }
  &.active {
    color: theme-var($text-normal);
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
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.25em 0;
  }
}
.cloud_account-add-btn {
  margin-left: 1.4em;
  &:hover {
    color: $col-warning;
  }
}
</style>

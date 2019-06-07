<template lang="pug">
  .user-profile
    base-switcher.sidebar_section(
      :tab-set-data="switcherData"
    )
      template(slot="firstTab")
        dl.user-info_list
          dt.user-info_name First name
          dd.user-info_data
            text-editable(
              :text-title="user.firstName"
              @change-title="editfirstName"
              )
          dt.user-info_name Last name
          dd.user-info_data
            text-editable(
              :text-title="user.lastName"
              @change-title="editlastName"
            )
          dt.user-info_name Email
          dd.user-info_data {{ user.email }}

      template(slot="secondTab")
        p secondTab
    .sidebar_action
      button.btn.btn--primary(type="button") Save

</template>

<script>
import BaseSwitcher     from "@/components/different/switcher.vue";
import TextEditable       from '@/components/base/text-editable.vue'


export default {
  name: "UserProfile",
  components: {BaseSwitcher, TextEditable},
  data() {
    return {
      switcherData: ['User', 'History'],
      user: {
        firstName: 'John',
        lastName: 'Doe',
        email: 'email@mail.com',
      }
    }
  },
  computed: {
    // userInfo() {
    //   return [
    //     {dt: 'First name' ,dd:}
    //   ]
    // }
  },
  methods: {
    editfirstName(newVal) {
      this.user.firstName = newVal
    },
    editlastName(newVal) {
      this.user.lastName = newVal
    },
    editemail(newVal) {
      this.user.email = newVal
    },
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .user-info_list {
    font-size: 1.4rem;
    display: flex;
    flex-wrap: wrap;
  }
  .user-info_name {
    width: 40%;
    color: $disable-txt;
    margin-bottom: 1rem;
  }
  .user-info_data {
    width: 60%;
    margin: 0;
    margin-bottom: 1rem;
  }
  .sidebar_action {
    text-align: center;
  }
</style>

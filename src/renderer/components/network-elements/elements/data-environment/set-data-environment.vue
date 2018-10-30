<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
      v-for="(tab, i) in tabs"
      :key="tab.i"
      @click="setTab(i)"
      :class="{'disable': tabSelected != i}"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body(
      :class="{'active': tabSelected == 0}"
      )
        .settings-layer
          .settings-layer_section
            base-select(:selectOptions="items")

      .popup_body(
        :class="{'active': tabSelected == 1}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              input.form_input(type="text" placeholder="c:")
              button.btn.btn--primary(type="button") Load

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  export default {
    name: 'SetDataData',
    mixins: [mixinSet],
    components: {

    },
    data() {
      return {
        items: ['Foo', 'Bar', 'Fizz', 'Buzz'],
        tabs: ['Gym', '<i class="icon icon-search"></i> Unity']
      }
    }
  }
</script>

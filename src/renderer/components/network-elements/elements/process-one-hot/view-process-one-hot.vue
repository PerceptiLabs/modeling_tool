<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
  data-component="ProcessOneHot"
  data-layer="OneHot_1"
  data-type="Other"
  v-tooltip:right="'One Hot'"
  v-tooltip-interactive:right="interactiveInfo"
  id="tutorial_one-hot"
  )
    i.icon.icon-one-hot

</template>

<script>
export default {
  name: 'ViewProcessOneHot',
  props: {
    draggable: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      interactiveInfo: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Lorem Ipsum:</div> is simply dummy text</br> the printing and typesetting  </br> industry. Lorem Ipsum </br>
                          <div class="tooltip-tutorial_bold">Has been the industry's standard</div>
                        </div>`
    }
  }
}
</script>

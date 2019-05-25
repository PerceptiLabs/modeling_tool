<template lang="pug">
  .btn.btn--layersbar.net-element-process(:draggable="draggable"
    data-component="ProcessGrayscale"
    data-layer="Grayscale_1"
    data-type="Other"
    v-tooltip:right="'Grayscale'"
    v-tooltip-interactive:right="interactiveInfo"
  )
    i.icon.icon-sieve

</template>

<script>
export default {
  name: 'ViewProcessGrayscale',
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

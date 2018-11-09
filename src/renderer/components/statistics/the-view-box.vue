<template lang="pug">
  section.network_info-section
    .info-section_head
      h3 ViewBox
    .info-section_main(v-if="viewBoxData")
      component(
        :is="viewBoxData.componentName"
        :elementData="viewBoxData.viewBox"
        )
</template>

<script>
import LearnDeepConnect from '@/components/network-elements/elements/learn-deep-connect/viewBox-learn-deep-connect.vue'
import LearnDeepConvolut from '@/components/network-elements/elements/learn-deep-convolut/viewBox-learn-deep-convolut.vue'
import DataData from '@/components/network-elements/elements/data-data/viewBox-data-data.vue'
export default {
  name: "TheViewBox",
  components: {
    LearnDeepConnect,
    LearnDeepConvolut,
    DataData
  },
  props: {
    elData: {
      type: Array,
      default: function () {
        return []
      }
    }
  },
  data() {
    return {

    }
  },
  mounted() {

  },
  methods: {

  },
  computed: {
    viewBoxData() {
      return this.elData.find((element, index, array)=>{
        if(element.layerType !== 'Training') {
          return element
        }
        else return false
      });
    }
  }
}
</script>

<style lang="scss" scoped>

</style>

<template lang="pug">
  section.network_info-section
    .info-section_head
      h3 Statistics
    .info-section_main(v-if="viewBoxData")
      component(
      :is="viewBoxData.componentName"
      :elementData="viewBoxData.viewBox"
      )
</template>

<script>
import TrainNormal from '@/components/network-elements/elements/train-normal/stat-train-normal.vue'
import LearnClassVectorMachine from '@/components/network-elements/elements/learn-class-vector-machine/stat-learn-class-vector-machine.vue'
export default {
  name: "TheStatistics",
  components: {TrainNormal, LearnClassVectorMachine},
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
  methods: {

  },
  computed: {
    viewBoxData() {
      return this.elData.find((element, index, array)=>{
        if(element.layerType === 'Training') {
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

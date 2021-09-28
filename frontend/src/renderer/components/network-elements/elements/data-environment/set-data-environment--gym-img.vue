<template lang="pug">
  .form_row(v-tooltip-interactive:right="interactiveInfo.actionSpace")
    chart-switch(
      key="1"
      :chart-label="chartLabel"
      :chart-data="imgData"
    )

</template>

<script>
  import ChartSwitch from "@/components/charts/chart-switch.vue";

  export default {
    name: 'SetDataEnvironmentGymImg',
    components: { ChartSwitch},
    props: {
      layerSettings:  {type: Object},
      layerId:        {type: String},
    },
    mounted() {
      this.getPreviewSample();
    },
    data() {
      return {
        imgData: null,
        interactiveInfo: {
          actionSpace: {
            title: 'Action Space',
            text: 'Number of different actions </br> you can take in the game'
          }
        }
      }
    },
    computed: {
      chartLabel() {
        //return `Action space: ${this.Mix_settingsData_actionSpace}`
        return `Action space:`
      }
    },
    watch: {
      'layerSettings.accessProperties.Atari': {
        handler(newVal) {
          if(newVal) {
            this.getPreviewSample();
          }
        },
        //immediate: true
      },
    },
    methods: {
      getPreviewSample() {
        this.$emit('apply-settings');
        this.$store.dispatch('mod_api/API_getPreviewSample', {layerId: this.layerId, varData: 'sample'})
          .then((data)=> {
            this.imgData = data;
          } )
      }
    },
    getData() {
      this.$store.dispatch('mod_api/API_getDataMeta', {layerId: this.layerId, settings: this.settings})
        .then((data) => {
            console.log(data);
        })
        .catch((err) => {
          console.error('getDataMeta', err);
        })
        .finally(()=> this.showSpinner = false)
    }
  }
</script>

<style lang="scss" scoped>
  
  .settings-layer_section {
    position: relative;
  }
</style>

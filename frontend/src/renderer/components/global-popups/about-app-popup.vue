<template lang="pug">
  .about-popup-wrapper(@click="closeModal")
    .about-box(@click.stop="() => null")
      img.close-cross(@click="closeModal" src="./../../../../static/img/close-blue-cross.svg") 
      .d-flex.flex-column.justify-content-center.align-items-center
        img.pl-logo(src="./../../../../static/img/perceptilabs-logo-icon.svg" alt="logos")
        img.pl-text(src="./../../../../static/img/perceptilabs-logo-text.svg" alt="logos")
        p.text Version {{appVersion}}
        p.text Last update {{appUpdateDate}}
        p.text © 2021 PerceptiLabs.
        p.text All rights reserved.
        a.link.about-popup-link.terms-link(href="https://perceptilabs.com/terms" target="_blank") License Terms 
        a.about-popup-link(href="https://forum.perceptilabs.com/" target="_blank") Forum
</template>
<script>
export default {
  name: 'AboutAppPopup',
  data: () => ({
    releases: []
  }),
  computed: {
    appVersion() {
      return this.$store.state.globalView.appVersion;
    },
    appUpdateDate() {
      return this.releases[this.appVersion] && this.releases[this.appVersion][0].upload_time ? new Date(this.releases[this.appVersion] && this.releases[this.appVersion][0].upload_time).toLocaleDateString() : "";
    },
  },
  mounted() {
    fetch('https://pypi.org/pypi/perceptilabs/json')
      .then((res) => res.json())
      .then((res) => {
        this.releases = res.releases
      });
  },
  methods: {
    closeModal() {
      this.$store.commit('globalView/set_showAppAbout', false);
    }
  }
}
</script>
<style lang="scss" scoped>
.about-popup-wrapper {
  position: fixed;
  z-index: 20;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.about-box {
  position: relative;
  min-width: 213px;
  padding-bottom: 18px;
  background: linear-gradient(308deg, #383F50 0%, #23252A 100%);
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
  border-radius: 2px;
}
.close-cross {
  position: absolute;
  cursor: pointer;
  top: 10px;
  right: 10px;
  width: 10px;
  height: 10px;
}
.pl-logo {
  width: 23px;
  margin-top: 18px;
}
.pl-text {
  margin-top: 8px;
  margin-bottom: 20px;
}
.text { 
  font-family: Nunito Sans;
  font-size: 12px;
  line-height: 16px;
  color: #FFFFFF;
  margin-bottom: 2px;
}
.terms-link {
  margin-top: 20px;
  margin-bottom: 3px;
  
}
.about-popup-link {
  color: #9BB2F6;
  font-size: 12px;
}
</style>
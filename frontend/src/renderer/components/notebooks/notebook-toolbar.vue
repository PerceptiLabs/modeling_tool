<template>
  <div class="toolbar-container">
    <div class="toolbar-buttons">
      <div class="cell save-button"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" focusable="false" width="1em" height="1em" style="-ms-transform: rotate(360deg); -webkit-transform: rotate(360deg); transform: rotate(360deg);" preserveAspectRatio="xMidYMid meet" viewBox="0 0 1536 1536"><path d="M384 1408h768v-384H384v384zm896 0h128V512q0-14-10-38.5t-20-34.5l-281-281q-10-10-34-20t-39-10v416q0 40-28 68t-68 28H352q-40 0-68-28t-28-68V128H128v1280h128V992q0-40 28-68t68-28h832q40 0 68 28t28 68v416zM896 480V160q0-13-9.5-22.5T864 128H672q-13 0-22.5 9.5T640 160v320q0 13 9.5 22.5T672 512h192q13 0 22.5-9.5T896 480zm640 32v928q0 40-28 68t-68 28H96q-40 0-68-28t-28-68V96q0-40 28-68T96 0h928q40 0 88 20t76 48l280 280q28 28 48 76t20 88z" fill="#626262"/><rect x="0" y="0" width="1536" height="1536" fill="rgba(0, 0, 0, 0)" /></svg></div>
      <div class="cell separater"></div>
      <div class="cell add-cell"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" focusable="false" width="1em" height="1em" style="-ms-transform: rotate(360deg); -webkit-transform: rotate(360deg); transform: rotate(360deg);" preserveAspectRatio="xMidYMid meet" viewBox="0 0 1408 1408"><path d="M1408 608v192q0 40-28 68t-68 28H896v416q0 40-28 68t-68 28H608q-40 0-68-28t-28-68V896H96q-40 0-68-28T0 800V608q0-40 28-68t68-28h416V96q0-40 28-68t68-28h192q40 0 68 28t28 68v416h416q40 0 68 28t28 68z" fill="#626262"/><rect x="0" y="0" width="1408" height="1408" fill="rgba(0, 0, 0, 0)" /></svg></div>
      <div class="cell separater"></div>
      <div class="cell cut-cell"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" focusable="false" width="1.28em" height="1em" style="-ms-transform: rotate(360deg); -webkit-transform: rotate(360deg); transform: rotate(360deg);" preserveAspectRatio="xMidYMid meet" viewBox="0 0 1792 1408"><path d="M960 640q26 0 45 19t19 45t-19 45t-45 19t-45-19t-19-45t19-45t45-19zm300 64l507 398q28 20 25 56q-5 35-35 51l-128 64q-13 7-29 7q-17 0-31-8L879 885l-110 66q-8 4-12 5q14 49 10 97q-7 77-56 147.5T579 1324q-132 84-277 84q-136 0-222-78q-90-84-79-207q7-76 56-147t131-124q132-84 278-84q83 0 151 31q9-13 22-22l122-73l-122-73q-13-9-22-22q-68 31-151 31q-146 0-278-84q-82-53-131-124T1 285q-5-59 15.5-113T80 79Q165 0 302 0q145 0 277 84q83 52 132 123t56 148q4 48-10 97q4 1 12 5l110 66l690-387q14-8 31-8q16 0 29 7l128 64q30 16 35 51q3 36-25 56zM579 444q46-42 21-108T494 219q-92-59-192-59q-74 0-113 36q-46 42-21 108t106 117q92 59 192 59q74 0 113-36zm-85 745q81-51 106-117t-21-108q-39-36-113-36q-100 0-192 59q-81 51-106 117t21 108q39 36 113 36q100 0 192-59zm178-613l96 58v-11q0-36 33-56l14-8l-79-47l-26 26q-3 3-10 11t-12 12q-2 2-4 3.5t-3 2.5zm224 224l96 32l736-576l-128-64l-768 431v113l-160 96l9 8q2 2 7 6q4 4 11 12t11 12l26 26zm704 416l128-64l-520-408l-177 138q-2 3-13 7z" fill="#626262"/><rect x="0" y="0" width="1792" height="1408" fill="rgba(0, 0, 0, 0)" /></svg></div>
      <div class="cell copy-cell"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" focusable="false" width="1em" height="1em" style="-ms-transform: rotate(360deg); -webkit-transform: rotate(360deg); transform: rotate(360deg);" preserveAspectRatio="xMidYMid meet" viewBox="0 0 1792 1792"><path d="M1696 384q40 0 68 28t28 68v1216q0 40-28 68t-68 28H736q-40 0-68-28t-28-68v-288H96q-40 0-68-28t-28-68V640q0-40 20-88t48-76L476 68q28-28 76-48t88-20h416q40 0 68 28t28 68v328q68-40 128-40h416zm-544 213L853 896h299V597zM512 213L213 512h299V213zm196 647l316-316V128H640v416q0 40-28 68t-68 28H128v640h512v-256q0-40 20-88t48-76zm956 804V512h-384v416q0 40-28 68t-68 28H768v640h896z" fill="#626262"/><rect x="0" y="0" width="1792" height="1792" fill="rgba(0, 0, 0, 0)" /></svg></div>
      <div class="cell paste-cell"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" focusable="false" width="1em" height="1em" style="-ms-transform: rotate(360deg); -webkit-transform: rotate(360deg); transform: rotate(360deg);" preserveAspectRatio="xMidYMid meet" viewBox="0 0 1792 1792"><path d="M768 1664h896v-640h-416q-40 0-68-28t-28-68V512H768v1152zm256-1440v-64q0-13-9.5-22.5T992 128H288q-13 0-22.5 9.5T256 160v64q0 13 9.5 22.5T288 256h704q13 0 22.5-9.5t9.5-22.5zm256 672h299l-299-299v299zm512 128v672q0 40-28 68t-68 28H736q-40 0-68-28t-28-68v-160H96q-40 0-68-28t-28-68V96q0-40 28-68T96 0h1088q40 0 68 28t28 68v328q21 13 36 28l408 408q28 28 48 76t20 88z" fill="#626262"/><rect x="0" y="0" width="1792" height="1792" fill="rgba(0, 0, 0, 0)" /></svg></div>
      <div class="cell separater"></div>
      <div class="cell move-cell-up"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" focusable="false" width="1.09em" height="1em" style="-ms-transform: rotate(360deg); -webkit-transform: rotate(360deg); transform: rotate(360deg);" preserveAspectRatio="xMidYMid meet" viewBox="0 0 1600 1472"><path d="M1579 779q0 51-37 90l-75 75q-38 38-91 38q-54 0-90-38L992 651v704q0 52-37.5 84.5T864 1472H736q-53 0-90.5-32.5T608 1355V651L314 944q-36 38-90 38t-90-38l-75-75q-38-38-38-90q0-53 38-91L710 37q35-37 90-37q54 0 91 37l651 651q37 39 37 91z" fill="#626262"/><rect x="0" y="0" width="1600" height="1472" fill="rgba(0, 0, 0, 0)" /></svg></div>
      <div class="cell move-cell-down"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" focusable="false" width="1.09em" height="1em" style="-ms-transform: rotate(360deg); -webkit-transform: rotate(360deg); transform: rotate(360deg);" preserveAspectRatio="xMidYMid meet" viewBox="0 0 1600 1472"><g transform="translate(0 1472) scale(1 -1)"><path d="M1579 779q0 51-37 90l-75 75q-38 38-91 38q-54 0-90-38L992 651v704q0 52-37.5 84.5T864 1472H736q-53 0-90.5-32.5T608 1355V651L314 944q-36 38-90 38t-90-38l-75-75q-38-38-38-90q0-53 38-91L710 37q35-37 90-37q54 0 91 37l651 651q37 39 37 91z" fill="#626262"/></g><rect x="0" y="0" width="1600" height="1472" fill="rgba(0, 0, 0, 0)" /></svg></div>
    </div>
    <div class="kernel-status">{{ (isSessionOnline ? 'Online' : 'Not online') }}</div>
  </div>
</template>

<script>
export default {
  props: {
    isSessionOnline: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      kernelTimerHandle: null
    };
  },
  methods: {
    checkKernelStatus() {
      console.log('checkKernelStatus');
    }
  },
  created() {
    clearInterval(this.kernelTimerHandle);
    this.kernelTimerHandle = setInterval(this.checkKernelStatus, 5001);
  },
  destroyed() {
    clearInterval(this.kernelTimerHandle);
  }
}
</script>

<style lang="scss" scoped>
.toolbar-container {
  max-width: 60rem;
  margin: 0 auto;

  display: flex;
  justify-content: space-between;
  align-items: center;

  padding: 2rem 0;
  z-index: 10;

  .toolbar-buttons {
    display: flex;
    flex-direction: row;

    .cell {
      display: flex;
      margin: 0 0.5rem;
    }

    .separater {
      content: '';
      margin: 0 0.5rem;
    }
  }
}
</style>

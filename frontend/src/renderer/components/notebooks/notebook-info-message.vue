<template>
  <div v-if="showInfoMessage" class="notebook-info-message-wrapper">
    <div>&nbsp;</div>
    <div class="notebook-info-message-text">This mode is currently only for viewing the code. To modify the code, either go through Open Code in the component settings or Export the model as a Jupyter Notebook.</div>
    <div class="notebook-info-message-close" @click="showInfoMessage = false">
      <svg xmlns="http://www.w3.org/2000/svg" width="9" height="9" viewBox="0 0 9 9" fill="none">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M0.146447 8.14699C-0.0488155 8.34226 -0.0488155 8.65884 0.146447 8.8541C0.341709 9.04936 0.658291 9.04936 0.853553 8.8541L4.50039 5.20727L8.14734 8.85422C8.34261 9.04949 8.65919 9.04949 8.85445 8.85422C9.04971 8.65896 9.04971 8.34238 8.85445 8.14712L5.20749 4.50016L8.8541 0.853553C9.04936 0.658291 9.04936 0.341709 8.8541 0.146447C8.65884 -0.0488156 8.34226 -0.0488154 8.147 0.146447L4.50039 3.79305L0.853901 0.146569C0.658639 -0.048693 0.342057 -0.048693 0.146795 0.146569C-0.0484675 0.341831 -0.0484675 0.658414 0.146795 0.853676L3.79328 4.50016L0.146447 8.14699Z" fill="#131B30"/>
      </svg>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
       showInfoMessage: true,
    }
  }
}
</script>
<style scss scoped>
.notebook-info-message-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  min-height: 25px;
  background-color: #B6C7FB;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 3;
  padding: 0 25px;
}

.notebook-info-message-text {
  font-family: Nunito Sans;
  font-size: 11px;
  font-style: normal;
  font-weight: 700;
  line-height: 18px;
  color: #131B30;
}
.notebook-info-message-close {
  margin-left: 10px;
  cursor: pointer;
}
</style>
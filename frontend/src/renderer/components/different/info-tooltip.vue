<template lang="pug">
  div.wrapper(:class="styleType")
    div.svg-wrapper(
      v-tooltip:wrap-text="text"
    )
      svg(:class="{'static': !text}" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none")
        path(fill-rule="evenodd" clip-rule="evenodd" d="M9 18C11.3869 18 13.6761 17.0518 15.364 15.364C17.0518 13.6761 18 11.3869 18 9C18 6.61305 17.0518 4.32387 15.364 2.63604C13.6761 0.948212 11.3869 0 9 0C6.61305 0 4.32387 0.948212 2.63604 2.63604C0.948212 4.32387 0 6.61305 0 9C0 11.3869 0.948212 13.6761 2.63604 15.364C4.32387 17.0518 6.61305 18 9 18ZM10.0463 7.4115L7.47 7.73438L7.37775 8.16187L7.884 8.25525C8.21475 8.334 8.28 8.45325 8.208 8.78288L7.37775 12.6844C7.1595 13.6935 7.49588 14.1683 8.28675 14.1683C8.89988 14.1683 9.612 13.8848 9.93488 13.4955L10.0339 13.0275C9.80888 13.2255 9.48037 13.3043 9.26213 13.3043C8.95275 13.3043 8.84025 13.0871 8.92013 12.7046L10.0463 7.4115ZM9 6.1875C9.29837 6.1875 9.58452 6.06897 9.7955 5.858C10.0065 5.64702 10.125 5.36087 10.125 5.0625C10.125 4.76413 10.0065 4.47798 9.7955 4.267C9.58452 4.05603 9.29837 3.9375 9 3.9375C8.70163 3.9375 8.41548 4.05603 8.2045 4.267C7.99353 4.47798 7.875 4.76413 7.875 5.0625C7.875 5.36087 7.99353 5.64702 8.2045 5.858C8.41548 6.06897 8.70163 6.1875 9 6.1875Z" fill="#6185EE")
    div.slot
      slot
  </div>
</template>
<script>
export default {
  name: "InfoTooltip",
  props: {
    text: {
      type: String,
      default: '',
    },
    styleType: {type: String, default: ''}
  },
}
</script>
<style scoped lang="scss">
.wrapper {
  display: flex;
  align-items: center;
}
.svg-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  margin-right: 5px;
}
svg {
  cursor: pointer;
  path {
    fill: #B6C7FB;
  }
  &:not(.static):hover {
    background: white;
    border-radius: 50%;
    path {
      fill: #131B30;
    }
  }
}

</style>
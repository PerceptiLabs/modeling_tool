<template>
  <div class="flex flex-col h-screen w-screen">
    <NavHeader />
    <div class="flex h-full w-full">
      <NavSidebar />
      <router-view class="flex-1"></router-view>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

import NavHeader from "./Nav/NavHeader.vue";
import NavSidebar from "./Nav/NavSidebar.vue";

export default defineComponent({
  components: { NavHeader, NavSidebar },
});
</script>

<style lang="scss" scoped></style>

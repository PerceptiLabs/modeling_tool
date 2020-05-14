<template lang="pug">
	.tabsets
		network-tabset
		statistics-tabset
</template>

<script>
import NetworkTabset from '@/components/workspace/tabset/workspace-tabset-network.vue'
import StatisticsTabset from '@/components/workspace/tabset/workspace-tabset-statistics.vue'

export default {
	components : {
		NetworkTabset,
		StatisticsTabset
	}
}

</script>

<style lang="scss" scoped>

.tabsets {
	display: flex;
}
</style>

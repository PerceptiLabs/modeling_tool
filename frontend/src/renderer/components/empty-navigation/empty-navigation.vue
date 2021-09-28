<template lang="pug">
	.empty-navigation
		.content(v-if="emptyNavigationMode==1")
			.circle
				img.img-folder(src="static/img/model-empty.svg")
			.row
				p.description(
					v-if="getModelCount===0"
					) It appears you have not built any models. <br/> Create a model to begin.
				p.description(
					v-if="getModelCount>0"
					) It appears you do not have any models open. <br/>Select or Create New model to continue.
				ul(v-if="getModelCount>0")
					.header Recently Opened
					li(
						v-for="model in workspaceContent"
						@click.stop="openModelID(model.networkID)"
					) {{model.networkName}}
				.d-flex.content-center
					router-link.btn.btn--secondary.mr-3(
						:to="{name: 'projects'}"
						v-if="getModelCount>0"
					) Go to Model Hub
					button.btn.btn--primary(
						@click="popupNewModel(true)"
					) Create New
		.content(v-else-if="emptyNavigationMode==2")
			.circle
				img.img-folder(src="static/img/stats-empty.svg")
			.row
				p.description(
					v-if="getModelCount===0"
					) It appears you have not built any models. <br/> Create a model to begin.
				p.description(
					v-if="getModelCount>0 && getAvailableStats.length===0"
					)   It appears you have not run any models. Run a model <br/>from Modeling Tool or Model Hub to view statistics.<br/><br/>
					img.info-image(src="static/img/info.png")
					span.fz-14 Only statistics from your current session is available.
				p.description(
					v-if="getModelCount>0 && getAvailableStats.length>0"
					)   It appears you do not have any statistics open.<br/>
					img.info-image(src="static/img/info.png")
					span.fz-14 Only statistics from your current session is available.<br/><br/>Following models can be opened:
				ul(v-if="getAvailableStats.length>0")
					.header Recently Opened
					li(
						v-for="model in getAvailableStats"
						@click.stop="openStatisticsID(model.networkID)"
					) {{model.networkName}}
				p.description(
					v-if="getAvailableStats.length>0"
					)   Or run a model to continue:
				.d-flex.content-center
					button.btn.btn--primary.mr-3(
						@click="goToModelView()"
						v-if="getModelCount>0"
					) Go to Modeling Tool
					router-link.btn.btn--secondary.mr-3(
						:to="{name: 'projects'}"
						v-if="getModelCount>0"
					) Go to Model Hub
					button.btn.btn--primary(v-if="getModelCount==0"
						@click="popupNewModel(true)"
					) Create New

</template>

<script>

import { mapActions, mapGetters } from 'vuex';

export default {
	name: 'EmptyNavigation',
	methods: {
		...mapActions({
			popupNewModel:       	'globalView/SET_newModelPopup',
			set_currentNetwork:  	'mod_workspace/SET_currentNetwork',
			SET_currentModelIndex:  'mod_workspace/SET_currentModelIndex',
			SET_currentStatsIndex:  'mod_workspace/SET_currentStatsIndex',
			SET_currentTestIndex:	'mod_workspace/SET_currentTestIndex',
			SET_emptyScreenMode:    'mod_empty-navigation/SET_emptyScreenMode',
			SET_openStatistics:		'mod_workspace/SET_openStatistics',
			SET_openTest: 			'mod_workspace/SET_openTest',
			closeStatsTestViews:    'mod_workspace/SET_statisticsAndTestToClosed',
		}),
		openModelID(networkID) {
			const index = this.workspaceContent.findIndex(wc => wc.networkID == networkID);
			this.set_currentNetwork(index > 0 ? index : 0);

			this.SET_emptyScreenMode(0);
			this.$store.commit('mod_workspace/update_network_meta', {key: 'hideModel', networkID: networkID, value: false});

			if(index !== -1) {
				this.$store.dispatch("mod_workspace/setViewType", 'model');

				this.SET_currentModelIndex(index);
			}
		},		
		openStatisticsID(networkID) {
			const index = this.workspaceContent.findIndex(wc => wc.networkID == networkID);
			this.set_currentNetwork(index > 0 ? index : 0);
			this.SET_openStatistics(true);


			this.SET_emptyScreenMode(0);
			this.$store.commit('mod_workspace/update_network_meta', {key: 'hideStatistics', networkID: networkID, value: false});
      this.$store.dispatch('mod_workspace/SET_chartsRequestsIfNeeded', networkID);
			if(index !== -1) {
				this.$store.dispatch("mod_workspace/setViewType", 'statistic');

				this.SET_currentStatsIndex(index);
			}
		},		
		goToModelView() {
				this.$store.dispatch("mod_workspace/setViewType", 'model');
        this.closeStatsTestViews({ networkId: this.currentNetworkId });

				this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 0);
		}
	},
	computed: {
		...mapGetters({
				emptyNavigationMode: 'mod_empty-navigation/getEmptyScreenMode',
		}),
		workspaceContent() {
			return this.$store.state.mod_workspace.workspaceContent;
		},
		currentNetworkId() {
			return this.$store.getters['mod_workspace/GET_currentNetworkId'];
		},
		getModelCount() {
			return this.workspaceContent.length;
		},
		getAvailableStats() {
			return this.workspaceContent.filter(wc => typeof wc.networkMeta.openStatistics === 'boolean');
		},
	}
}
</script>

<style lang="scss" scoped>
    .empty-navigation {
        width: 100%;
        height: 100%;
        // background: rgba(0, 0, 0, 0.25);
        // opacity: 0.8;

		.circle {
			width: 150px;
			height: 150px;
			border-radius: 50%;
			margin-bottom: 20px;
			display: flex;
			justify-content: center;
			align-items: center;
			background: theme-var($neutral-7);
		}
        .content {  
			display: flex;
			justify-content: center;
			align-items: center;
			flex-direction: column;
			height: 100%;

            .row {
                width: 50%;

                img {
                    margin-right: 140px;
                }
            }
        }
				
        p {
            font-family: Nunito Sans;
            font-style: normal;
            font-weight: 600;
            font-size: 16px;
            line-height: 22px;
            margin-bottom: 20px;
			text-align: center;
        }

        ul {
            max-height: 220px;
            padding: 0;
            margin-bottom: 35px;
            overflow: hidden;
			width: 335px;

			margin-right: auto;
			margin-left: auto;

            li, .header {
                padding: 12px 0px 12px 30px;
                border-bottom: 1px solid #3A485A;
                list-style: none;
                font-family: Nunito Sans;
                font-weight: normal;
                font-size: 16px;
                display: flex;
                align-items: center;
            }
            li:hover {
				background: theme-var($neutral-6);
            }
        }
    }
		.info-image {
			margin-right: 10px !important;
			vertical-align: top;
   		margin-top: 2px;
		}
		.fz-14 {
			font-size: 14px;
		}
		.mr-3 {
			margin-right: 16px;
		}
		.content-center {
			justify-content: center;
		}
</style>
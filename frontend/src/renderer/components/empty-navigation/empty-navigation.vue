<template lang="pug">
	.empty-navigation
		.content.d-flex(v-if="emptyNavigationMode==1")
			.row 
				img.img-folder(src="static/img/model-empty.png")
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
				.d-flex
					router-link.nav-link(
						:to="{name: 'projects'}"
						v-if="getModelCount>0"
					) Go to Model Hub
					button(
						@click="popupNewModel(true)"
					) Create New
		.content.d-flex(v-else-if="emptyNavigationMode==2")
			.row 
				img.img-folder(src="static/img/stats-empty.png")
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
				.d-flex
					button(
						@click="goToModelView()"
						v-if="getModelCount>0"
					) Go to Modeling Tool
					router-link.nav-link(
						:to="{name: 'projects'}"
						v-if="getModelCount>0"
					) Go to Model Hub
					button(v-if="getModelCount==0"
						@click="popupNewModel(true)"
					) Create New
		.content.d-flex(v-else-if="emptyNavigationMode==3")
			.row 
				img.img-folder(src="static/img/test-empty.png")
			.row
				p.description(
					v-if="getModelCount===0"
					) It appears you have not built any models. <br/> Create a model to begin.
				p.description(
					v-if="getModelCount>0 && getAvailableTests.length===0"
					)   It appears you have not run any models. Run a model <br/>from Modeling Tool or Model Hub to view statistics.
				p.description(
					v-if="getAvailableTests.length>0"
					)   It appears you do not have any tests open.<br/> Following models can be opened:
				ul(v-if="getAvailableTests.length>0")
					.header Recently Opened
					li(
						v-for="model in getAvailableTests"
						@click.stop="openTestID(model.networkID)"
					) {{model.networkName}}
				p.description(
					v-if="getAvailableTests.length>0"
					)   Or run a model to continue:
					
				.d-flex
					button(
						@click="goToModelView()"
						v-if="getModelCount>0"
					) Go to Modeling Tool
					router-link.nav-link(
						:to="{name: 'projects'}"
						v-if="getModelCount>0"
					) Go to Model Hub
					button(v-if="getModelCount==0"
						@click="popupNewModel(true)"
					) Create New

</template>

<script>

// import Vue from 'vue';
import { mapActions, mapGetters } from 'vuex';
import { stringifyNetworkObjects, promiseWithTimeout } from '@/core/helpers';

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
		openTestID(networkID) {
			const index = this.workspaceContent.findIndex(wc => wc.networkID == networkID);
			console.log("Selected Test index", index);
			this.set_currentNetwork(index > 0 ? index : 0);
			this.SET_openTest(true);
			
			this.SET_emptyScreenMode(0);
			this.$store.commit('mod_workspace/update_network_meta', {key: 'hideTest', networkID: networkID, value: false});


			if(index !== -1) {
				this.$store.dispatch("mod_workspace/setViewType", 'test');
				this.SET_currentTestIndex(index);
			}
		},		
		goToModelView() {
				this.$store.dispatch("mod_workspace/setViewType", 'model');
				// this.SET_openStatistics(false);
				// this.SET_openTest(false);
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
		getAvailableTests() {
			return this.workspaceContent.filter(wc => typeof wc.networkMeta.openTest === 'boolean');
		}
	}
}
</script>

<style lang="scss" scoped>
    .empty-navigation {
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.25);
        opacity: 0.8;
        color: #B6C7FB;
        display: flex;
        justify-content: center;
        align-items: center;

        .content {
            align-items: center;            

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
        }

        button, .nav-link {
            background: rgba(54, 68, 106, 0.25);
            height: 25px;
            border: 1px solid rgba(182, 199, 251, 0.5);
            box-sizing: border-box;
            border-radius: 2px;
            font-family: Nunito Sans;
            font-weight: 600;
            font-size: 12px;
            line-height: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #B6C7FB;
            margin-right: 10px;
            padding: 10px;
            // box-shadow: 0px 3px rgba(0,0,0,0.3);

            &:hover {
                background-color: #6185EE;
                color: white;
            }
        }

        ul {
            max-height: 130px;
            padding: 0;
            margin-bottom: 35px;
            overflow: hidden;

            li, .header {
                padding-left: 30px;
                border-bottom: 1px solid #363E51;
                list-style: none;
                font-family: Nunito Sans;
                font-weight: normal;
                font-size: 12px;
                line-height: 16px;
                color: #C4C4C4;
                width: 335px;
                height: 26px;
                display: flex;
                align-items: center;
            }
            li {
                color: #E1E1E1;
            }
            li:hover {
                background: #6185EE;
                color:white;
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
</style>
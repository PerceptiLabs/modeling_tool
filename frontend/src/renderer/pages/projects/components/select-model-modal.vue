<template lang="pug">
    div.select-model-modal(
            :data-tutorial-target="'tutorial-create-model-new-model'"
        )
        .header 
            .close-cross(@click="closeModal(true)")
            span New Model
        .main-wrapper
            template(v-if="!isTF2XEnabled || !isDataWizardEnabled")
                .main-templates
                    .main-templates-header
                        h3 Templates
                        //- div.search-template
                        //-     img(src="./../../../../../static/img/search-models.svg")
                        //-     input(type='text' placeholder="Search")
                    .main-templates-items
                        .template-item(
                            :class="{'is-selected': (chosenTemplate === -1)}"
                            @click="choseTemplate(-1)"
                        )
                            div.template-image
                                svg(width="50" height="50" viewBox="-10 -10 50 50" fill="none" xmlns="http://www.w3.org/2000/svg")
                                    rect(x="0.5" y="0.5" width="32.3333" height="32.3333" rx="1.5" stroke="#C4C4C4" stroke-opacity="0.8")
                                    rect(x="7.16797" y="7.16602" width="32.3333" height="32.3333" rx="1.5" fill="#383F50" stroke="#C4C4C4")
                                    path(d="M29.79 23.9637H24.2527V29.4873H22.4298V23.9637H16.9062V22.1271H22.4298V16.6035H24.2527V22.1271H29.79V23.9637Z" fill="#C4C4C4")


                            span.template-name Empty
                        .template-item(
                            v-for="(temp, i) in basicTemplates"
                            :class="{'is-selected': (chosenTemplate === i)}"
                            @click="choseTemplate(i)"
                        )
                            div.template-image(v-if="temp.imgPath")
                                img(:src="temp.imgPath" :alt="temp.title")
                            span.template-name {{ temp.title }}
            template(v-else)
                .main-file-structure-section
                    .main-file-structure-header
                        h3 File structure
                        //- div.search-template
                        //-     img(src="./../../../../../static/img/search-models.svg")
                        //-     input(type='text' placeholder="Search")
                    .main-file-structure-contents
                        .load-contents-group(v-if="!dataset")
                            button.action-button(@click="openFilePicker('setDataPath')") Load data
                        .dataset-settings(v-if="dataset")
                          base-checkbox.light-text(v-model="datasetSettings.randomizedPartitions") Randomized partitions
                        csv-table(v-if="dataset" :dataSet="dataset" @update="handleCSVDataTypeUpdates")        
            .main-actions 
                div  
                    h4.presets-text Name:
                    .model-title-input-wrapper
                        input.model-title-input(
                            type="text"
                            v-model="modelName"
                            @keyup="onModelNameKeyup"
                            :data-tutorial-target="'tutorial-create-model-model-name'")
                    h4.presets-text Model Path
                    .mode-path-wrapper
                        .form_holder
                            .form_row
                                input.form_input(
                                    readonly
                                    type="text" 
                                    v-model="modelPath" 
                                    :data-tutorial-target="'tutorial-create-model-model-path'")
                                    
                                button.btn.btn--dark-blue-rev(type="button" @click="openFilePicker") Browse
                    p.label(v-if="chosenTemplate > -1 && chosenTemplate !== null") Preview:
                    .screenshoot-container(v-if="chosenTemplate > -1 && chosenTemplate !== null")
                        img(:src="`./../../../../../static/img/${basicTemplates[chosenTemplate].screenshoot}`" class="image-screenshoot")
                    p.label(v-if="chosenTemplate !== null") Description:
                    perfect-scrollbar.template-description(
                        v-if="chosenTemplate !== null"
                        :data-tutorial-target="'tutorial-create-model-description'"
                        ) 
                        span(v-if="chosenTemplate > -1") {{basicTemplates[chosenTemplate] && basicTemplates[chosenTemplate].description}}
                        span(v-else) {{'This is an empty model which acts as a clean slate if you want to start from scratch'}}
                    p.template-description-else(
                        v-else
                        :data-tutorial-target="'tutorial-create-model-description'"
                    )
                .main-actions-buttons
                    button.action-button.mr-5(@click="closeModal(true)") Cancel
                    button#create-model-btn.action-button.create-btn.ml-5(
                        :class="{'is-disabled': isDisableCreateAction()}"
                        @click="debouncedCreateModelFunction()"
                    )
                        svg.plus-icon(width='17' height='17' viewbox='0 0 17 17' fill='none' xmlns='http://www.w3.org/2000/svg')
                            path(d='M11.7924 8.82157H8.96839V11.6386H8.0387V8.82157H5.22168V7.88489H8.0387V5.06787H8.96839V7.88489H11.7924V8.82157Z' fill='white')
                            rect(x='0.5' y='0.5' width='16' height='16' rx='1.5' stroke='white')
                        | Create
        file-picker-popup(
            v-if="showFilePickerPopup"
            :popupTitle="filepickerOptions.popupTitle"
            :filePickerType="filepickerOptions.filePickerType"
            :startupFolder="filepickerOptions.startupFolder"
            :confirmCallback="filepickerOptions.confirmCallback"
            :cancelCallback="closePopup"
        )
</template>
<script>
    import imageClassification    from '@/core/basic-template/image-classification.js'
    import reinforcementLearning  from '@/core/basic-template/reinforcement-learning.js'
    import linearRegression       from '@/core/basic-template/linear-regression.js'
    import objectDetection        from '@/core/basic-template/object-detection.js'
    import ganTemplate            from '@/core/basic-template/gan-template.js'
    import FilePickerPopup        from "@/components/global-popups/file-picker-popup.vue";
    import CsvTable               from "@/components/different/csv-table.vue";

    import { mapActions, mapState, mapGetters } from 'vuex';
    import { convertModelRecommendationToVisNodeEdgeList, createVisNetwork } from '@/core/helpers/layer-positioning-helper';
    import { buildLayers } from '@/core/helpers/layer-creation-helper';

    import { debounce } from '@/core/helpers'
    import cloneDeep from 'lodash.clonedeep';

    import { doesDirExist as fileserver_doesDirExist } from '@/core/apiFileserver';
    import { getFolderContent as fileserver_getFolderContent } from '@/core/apiFileserver';
    import { getResolvedDir as fileserver_getResolvedDir } from '@/core/apiFileserver';
    import { getRootFolder as fileserver_getRootFolder } from '@/core/apiFileserver';
    import { getFileContent as fileserver_getFileContent } from '@/core/apiFileserver';

export default {
    name: 'SelectModelModal',
    components: { FilePickerPopup, CsvTable },
    data: function() {
        return {
            basicTemplates: [
            {
                title: 'Image Classification CNN',
                imgPath: './static/img/project-page/classification.png',
                template: imageClassification,
                description: 'This is a simple image classification template, perfect for datasets such as MNIST. The standard dataset included with this template is an MNIST dataset where the input is an array of 784 grayscale pixel values and 10 unique label values (integers 0-9). The model consists of a reshaping component, a convolutional layer, and a fully connected output layer with 10 neurons. Because of the reshaping component it requries the input data to be 784 or a form thereof (28x28, for example). The labels must be integers ranging from 0 to 9 to be compatible with the one hot encoding that is applied to the labels.',
                screenshoot: 'template_image_classification.png'
            },
            {
                title: 'Linear Regression',
                imgPath: './static/img/project-page/linear-regression.png',
                template: linearRegression,
                description: `This is a template for linear regression, where it tries to create a line of best fit for the datapoints you load. The standard dataset is a one-dimensional input value and one-dimensional labels. The input data can be multidimensional, but our visualizations will display the data in one dimension. The labels data must be one-dimensional as they represent the value of the input data. The model is built as a single fully connected layer with one neuron as output.`,
                screenshoot: 'template_linear_regression.png'
            },
            {
                title: 'DQN',
                imgPath: './static/img/project-page/reinforcement-learning.png',
                template: reinforcementLearning,
                description: `This is a template for Reinforcement Learning consisting of one grayscale component, one convolutional layer and one fully connected layer as output. This template uses Q learning on Atari Gym games, where it is set up to play breakout. To play another game, you will change the neurons in the fully connected layer to match the number of possible actions in the actionspace, which you can see in the Environment component.`,
                screenshoot: 'template_dqn.png'
            },
            {
                title: 'YOLO V1',
                imgPath: './static/img/project-page/object-detection.png',
                template: objectDetection,
                description: `This is a template of the Object Detection model YOLO. It trains on a custom-built dataset containing different shapes as standard. Since it consists of only convolutional layers, any input data will work to train on, as long as the label data matches the input data.`,
                screenshoot: 'template_yolo.png'
            },
            {
                title: 'GAN',
                imgPath: './static/img/project-page/GAN.png',
                template: ganTemplate,
                description: `This is a template for a Generative Adversarial Network (GAN) where it trains on the MNIST data as a standard. The model consists of a generative network and a discriminative network, as well as a switch layer which switches between the generated image and real image.`,
                screenshoot: 'template_gan.png'
            },
            ],
            chosenTemplate: null,
            modelName: '',
            description: '',
            modelPath: '',
            showFilePickerPopup: false,
            hasChangedModelName: false,
            csvData: null, // parsed dataset and meta
            dataset: null,
            datasetPath: null,
	          datasetSettings: {
		            randomizedPartitions: true
      	    },	
            filepickerOptions: {
                popupTitle: '',
                filePickerType: '',
                startupFolder: '',
                confirmCallback: ''
            },
            debouncedCreateModelFunction: null
        }
    },
    computed: {
        ...mapState({
          currentProjectId:     state => state.mod_project.currentProject,  
          workspaces:           state => state.mod_workspace.workspaceContent,
        }),
        ...mapGetters({
            currentProject:     'mod_project/GET_project',
            projectPath:        'mod_project/GET_projectPath',
            currentNetworkId:   'mod_workspace/GET_currentNetworkId',
            defaultTemplate:    'mod_workspace/GET_defaultNetworkTemplate'
        }),
        isTF2XEnabled() {
            return process.env.ENABLE_TF2X === 'true';
        },
        isDataWizardEnabled() {
            return process.env.ENABLE_DATA_WIZARD === 'true';
        }
    },
    mounted() {
        this.modelPath = this.projectPath;
        document.addEventListener('keyup', this.handleKeyup);

        this.debouncedCreateModelFunction = debounce(_ => {
            this.createModel();
        }, 1000);
    },
    beforeDestroy() {
        document.removeEventListener('keyup', this.handleKeyup);
    },
    methods: {
        ...mapActions({
            addNetwork:                 'mod_workspace/ADD_network',
            closeStatsTestViews:        'mod_workspace/SET_statisticsAndTestToClosed',
            createProjectModel:         'mod_project/createProjectModel',
            getModelMeta:               'mod_project/getModel',
            getProjects:                'mod_project/getProjects',
            showErrorPopup:             'globalView/GP_errorPopup',
            setCurrentView:             'mod_tutorials/setCurrentView',
            setNextStep:                'mod_tutorials/setNextStep',
            setChecklistItemComplete:   'mod_tutorials/setChecklistItemComplete',
            getModelRecommendation:     'mod_api/API_getModelRecommendation',
            
        }),
        closeModal(triggerViewChange = false) {
            this.$store.dispatch('globalView/SET_newModelPopup', false);

            if (triggerViewChange)
            {
                this.setCurrentView('tutorial-model-hub-view');
            }
        },
        choseTemplate(index) {
            this.chosenTemplate = index;
            this.autoPopulateName();

            this.setNextStep({currentStep:'tutorial-create-model-new-model'});
        },
        async autoPopulateName() {
            if (this.modelName && this.hasChangedModelName) { return; }
            if (!this.modelPath) { return; }

            const resolvedDir = await fileserver_getResolvedDir(this.modelPath);
            const dirContents = await fileserver_getFolderContent(resolvedDir);

            let namePrefix = '';
            if (this.chosenTemplate && // null case for TF2X models
                this.chosenTemplate >= 0 &&
                this.chosenTemplate <= this.basicTemplates.length - 1) {
                namePrefix = this.basicTemplates[this.chosenTemplate].title
                    .replace(' ', '');
            } else {
                namePrefix = 'Model';
            }
             
            const highestSuffix = dirContents.dirs
                .filter(d => d.startsWith(namePrefix))
                .map(d => d.replace(`${namePrefix} `, ''))
                .map(d => parseInt(d))
                .filter(suffixNum => !isNaN(suffixNum))
                .reduce((max, curr) => Math.max(max, curr), 0);

            this.modelName = `${namePrefix} ${highestSuffix + 1}`
        },
        isDisableCreateAction() {

            if (this.isTF2XEnabled) {
                const { modelName,  csvData} = this;
                return (!csvData || !modelName);
            } else {
                const { chosenTemplate, modelName, basicTemplates } = this;
                return ((chosenTemplate === null) || !modelName);
            }
        },
        async createModel() {
            
            if (this.isTF2XEnabled && this.isDataWizardEnabled) {
                await this.createModelTF2X();
            } else {
                await this.createModelTF1X();
            }
        },
        async createModelTF2X() {

            if (!this.csvData) { return; }

            const { modelName, modelPath } = this;

            // Check validity
            if(!await this.isValidModelName(modelName)) {
                // TODO: showErrorPopup closes all popups, need to change this logic for UX
                // Annoying to have to type everything in again
                this.showErrorPopup(`The model name "${modelName}" already exists.`);
                this.setCurrentView('tutorial-model-hub-view');
                return;
            }

            if(!await this.isValidDirName(modelName, modelPath)) {
                this.showErrorPopup(`The "${modelName}" folder already exists at "${modelPath}".`);
                this.setCurrentView('tutorial-model-hub-view');
                return;
            }

            await this.$store.dispatch('mod_datasetSettings/setCurrentDataset', this.datasetPath);
            const datasetSettings = {
                'randomizedPartitions': this.datasetSettings.randomizedPartitions, 
                'featureSpecs': this.formatCSVTypesIntoKernelFormat()
             };
             
            await this.$store.dispatch('mod_datasetSettings/setDatasetSettings', {
                datasetPath: this.datasetPath, 
                settings: datasetSettings
             });
            const payload = this.$store.getters['mod_datasetSettings/getCurrentDatasetSettings']();
            const modelRecommendation = await this.getModelRecommendation(payload);
            
            const inputData = convertModelRecommendationToVisNodeEdgeList(modelRecommendation);
            const network = createVisNetwork(inputData);

            // Wait till the 'stabilized' event has fired
            await new Promise(resolve => network.on('stabilized', async (data) => resolve()));

            // Creating the project/network entry in rygg
            const apiMeta = await this.createProjectModel({
                name: modelName,
                project: this.currentProjectId,
                location: `${this.modelPath}/${modelName}`,
            });
            
            // Creating the networkElementList for the network
            var ids = inputData.nodes.getIds();
            var nodePositions = network.getPositions(ids);
            const layers = await buildLayers(modelRecommendation, nodePositions);
            
            // Creating network and adding the prepped layer to it
            const newNetwork = cloneDeep(this.defaultTemplate);
            newNetwork.networkID = apiMeta.model_id;
            newNetwork.networkName = modelName;
            newNetwork.networkElementList = layers;

            // Adding network to workspace
            await this.addNetwork({ network: newNetwork,  apiMeta });

            // Swapping view so that the newly created model is shown
            // TODO: break apart this views
            await this.$store.dispatch('mod_workspace/SET_statisticsAndTestToClosed',{ networkId: this.currentNetworkId });
            await this.$store.dispatch('mod_workspace/SET_currentModelIndexByNetworkId', apiMeta.model_id);
            await this.$store.dispatch('mod_workspace/setViewType', 'model');
            
            this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 0);
            this.setChecklistItemComplete({ itemId: 'createModel' });

            this.$nextTick(() => {
                this.setCurrentView('tutorial-workspace-view');
            });

            this.closeModal(false);
        },
        async createModelTF1X() {
            const { chosenTemplate, modelName, basicTemplates } = this;
            if((chosenTemplate === null) || !modelName)  return

            // TODO: test with isValidModelName
            // check if models name already exists
            const promiseArray = 
                this.currentProject.models
                    .map(x => this.getModelMeta(x));
            const modelMeta = await Promise.all(promiseArray);
            const rootPath = await fileserver_getRootFolder();
            const modelNames = modelMeta.map(x => x.name);
            if(modelNames.indexOf(modelName) !== -1) {
                this.showErrorPopup(`The model name "${modelName}" already exists.`);
                this.setCurrentView('tutorial-model-hub-view');
                return;
            }
            
            // TODO: test with isValidDirName
            const dirAlreadyExist = await fileserver_doesDirExist(`${this.modelPath}/${modelName}`);
            if(dirAlreadyExist) {
                this.showErrorPopup(`The "${modelName}" folder already exists at "${this.modelPath}".`);
                this.setCurrentView('tutorial-model-hub-view');
                return;
            }

            let modelType;
            let newModelId;

            this.createProjectModel({
                name: modelName,
                project: this.currentProjectId,
                location: `${this.modelPath}/${modelName}`,
            }).then(apiMeta => {
                newModelId = apiMeta.model_id;

                if(chosenTemplate === -1) {
                    const defaultTemplate = cloneDeep(this.defaultTemplate);
                    defaultTemplate.networkID = apiMeta.model_id;
                    defaultTemplate.networkName = modelName;
                    
                    modelType = 'Custom';

                    return this.addNetwork({ network: defaultTemplate,  apiMeta });
                } else {
                    let template = cloneDeep(basicTemplates[chosenTemplate].template.network);

                    const newRootPath = rootPath.replace(/\\/g, "/");
                    this.convertToAbsolutePath(template.networkElementList, newRootPath);
                    template.networkName = modelName;
                    template.networkID = apiMeta.model_id;

                    modelType = basicTemplates[chosenTemplate].title;

                    return this.addNetwork({network: template, apiMeta});
                }
            }).then(_ => {
                this.getProjects();
                this.$store.dispatch('mod_tracker/EVENT_modelCreation', modelType, {root: true});

                this.closeStatsTestViews({ networkId: this.currentNetworkId });

                this.$store.dispatch("mod_workspace/SET_currentModelIndexByNetworkId", newModelId);
                this.$store.dispatch('mod_workspace/setViewType', 'model');
                
                this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 0);
                this.setChecklistItemComplete({ itemId: 'createModel' });

                
                // closing model will invoke:
                // setCurrentView('tutorial-model-hub-view');
                // hence the next tick
                this.$nextTick(() => {
                    this.setCurrentView('tutorial-workspace-view');
                });

                this.closeModal(false);
            });
        },
        openFilePicker(openFilePickerReason) {

            if (openFilePickerReason === 'setDataPath') {
                this.filepickerOptions.popupTitle = 'Choose data to load';
                this.filepickerOptions.filePickerType = 'multimode';
                this.filepickerOptions.startupFolder = this.modelPath;
                this.filepickerOptions.confirmCallback = this.handleDataPathUpdates;
            } else {    
                this.filepickerOptions.popupTitle = 'Choose Model path';
                this.filepickerOptions.filePickerType = 'folder';
                this.filepickerOptions.startupFolder = this.modelPath;
                this.filepickerOptions.confirmCallback = this.updateModelPath;

                this.setNextStep({currentStep:'tutorial-create-model-model-path'});
            }
            this.showFilePickerPopup = true;                
        },
        closePopup() {
            this.showFilePickerPopup = false;
        },
        updateModelPath(filepath) {
            this.modelPath = filepath && filepath[0] ? filepath[0] : '';
            this.showFilePickerPopup = false;
        },
        convertToAbsolutePath(elementList, rootPath) {
            const suffix = "/";

            for(var el in elementList) {
                if (elementList[el].layerType === "Data" && elementList[el].layerSettings.accessProperties && elementList[el].layerSettings.accessProperties.Sources) {
                    if (elementList[el].layerSettings.accessProperties.Sources.length) {
                        elementList[el].layerSettings.accessProperties.Sources.forEach(item => {
                            item.path = rootPath + suffix + 'tutorial_data' + suffix + item.path;
                        });
                    }
                }
            }
        },
        handleKeyup(event) {
          if (event.key === "Escape") {
            event.stopPropagation();
            if(this.showFilePickerPopup) {
              this.showFilePickerPopup = false;
            } else {
              this.closeModal(true);
            }
          } else if (event.key === "Enter" && !this.isDisableCreateAction()) {
            event.stopPropagation();
            this.debouncedCreateModelFunction();
            this.chosenTemplate = null;
            this.modelName = '';
          }
        },
        onModelNameKeyup() {
            if (this.modelName === '') {
                this.hasChangedModelName = false;
            } else {
                this.hasChangedModelName = true;
            }

            this.setNextStep({currentStep:'tutorial-create-model-model-name'});
        },
        async handleDataPathUpdates(dataPath) {
            if (!dataPath || !dataPath.length || dataPath[0].type !== 'file') {
                this.showFilePickerPopup = false;
                return;
            }

            const fileContents = await fileserver_getFileContent(`${dataPath[0].path}`);

            if (fileContents && fileContents.file_contents) {
                this.dataset = fileContents.file_contents;
                this.datasetPath = dataPath[0].path;
                this.autoPopulateName();
            }

            this.showFilePickerPopup = false;
        },
        handleCSVDataTypeUpdates(payload) {
            this.csvData = payload;
        },
        formatCSVTypesIntoKernelFormat() {
            const payload={};

            for(const [idx, val] of this.csvData.columnNames.entries()) {
                const sanitizedVal=val.replace(/^\n|\n$/g, '')
                payload[sanitizedVal]={}
                payload[sanitizedVal]['csv_path']=this.datasetPath
                payload[sanitizedVal]['iotype']=this.csvData.ioTypes[idx],
                payload[sanitizedVal]['datatype']=this.csvData.dataTypes[idx]
            }
            return payload
        },
        async isValidModelName(modelName) {
            if(!modelName) { return; }

            const promiseArray = 
                this.currentProject.models
                    .map(x => this.getModelMeta(x));
            const modelMeta = await Promise.all(promiseArray);
            const modelNames = modelMeta.map(x => x.name);

            // Making sure name is not already in the list
            return modelNames.indexOf(modelName) === -1;            
        },
        async isValidDirName(modelName, modelPath) {
            const dirAlreadyExist = await fileserver_doesDirExist(`${modelPath}/${modelName}`);
            
            return !dirAlreadyExist;
        }
    },
}
</script>
<style lang="scss" scoped>
    .select-model-modal {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        min-width: 849px;
        max-width: 80vw;
    }
    .label {
        font-family: Nunito Sans;
        font-style: normal;
        font-weight: normal;
        font-size: 12px;
        line-height: 16px;
        color: #E1E1E1;
        display: flex;
        align-items: center;        
        padding-left: 20px;
    }
    .header {
        position: relative;
        height: 38px;
        display: flex;
        justify-content: center;
        align-items: center;
        
        background-color: rgb(20, 28, 49);
        border: 1px solid rgba(97, 133, 238, 0.4);
        border-radius: 2px 2px 0px 0px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.25);

        font-size: 14px;
        line-height: 19px;
        text-align: center;
        font-family: Nunito Sans;
        font-style: normal;
        font-weight: 600;
        color: #B6C7FB;
        
    }
    .main-wrapper {
        display: flex;
        
    }
    .main-templates {
        width: 610px;
        padding-bottom: 120px;

        background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
        border: 1px solid rgba(97, 133, 238, 0.4);
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
        border-radius: 0;
        min-height: 520px;
        // border-right-width: 0;
        border-bottom-left-radius: 2px;
    }
    .main-templates-header {
        padding: 23px 30px;
        display: flex;
        align-items: center;
        justify-content: space-around
        h3  {
            font-family: Nunito Sans;
            font-size: 16px;
            line-height: 22px;
            color: #E1E1E1;
        }
        .search-template {
            width: 100%;
            position: relative;
            margin-left: 140px;
            img {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                left: 12px;
            }
            input {
                width: 100%;
                border: 1px solid #4D556A;
                box-sizing: border-box;
                border-radius: 2px;
                background: transparent;
                height: 30px;
                padding-left: 42px;
            }
        }
    
    }
    .main-templates-items {
        padding: 0 30px;
        margin-top: 33px;
        display: flex;
        flex-wrap: wrap;
        justify-content: start;
    
    }
    .template-item {
        cursor: pointer;
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        background: rgba(#383F50, 0.8);
        border-radius: 2px;
        height: 120px;
        margin-bottom: 10px;
        margin-right: 7px;
        width: calc(100% * (1/4) - 7.5px);
        border: 3px solid transparent;
        &:hover {
            background: rgba(#383F50, 1);
        }
        &.is-selected {
            border: 3px solid #1473e6;
            border-radius: 3px;
        }
    }
    .main-file-structure-section {
        box-sizing: border-box;
        width: 610px;
        padding-bottom: 120px;

        background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
        border: 1px solid rgba(97, 133, 238, 0.4);
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
        border-radius: 0;
        min-height: 520px;
        // border-right-width: 0;
        border-bottom-left-radius: 2px;
    }
    .main-file-structure-header {
        padding: 23px 30px;
        display: flex;
        align-items: center;
        justify-content: space-around
        h3  {
            font-family: Nunito Sans;
            font-size: 16px;
            line-height: 22px;
            color: #E1E1E1;
        }
        .search-template {
            width: 100%;
            position: relative;
            margin-left: 140px;
            img {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                left: 12px;
            }
            input {
                width: 100%;
                border: 1px solid #4D556A;
                box-sizing: border-box;
                border-radius: 2px;
                background: transparent;
                height: 30px;
                padding-left: 42px;
            }
        }
    
    }
    .main-file-structure-contents {
        width: 100%;
        height: 100%;
        padding: 0 30px;
        // margin-top: 33px;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
    
        & > .load-contents-group > button {
            height: 100%;
            line-height: 100%;

            text-align: center;
            padding: 1.5rem;
        }

        & > .dataset-settings {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 1rem;
            width: 100%;

            .custom-checkbox {
                display: flex;
                justify-content: flex-end;
                cursor: pointer;
            } 
        }

    }
    .main-actions {
        display: flex;
        flex-direction: column;
        width: 300px;

        background: #363E51;
        border: 1px solid rgba(97, 133, 238, 0.4);
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
        // border-radius: 2px;
        border-bottom-right-radius: 2px;
    }

    .presets-text {
        padding: 20px 20px 0;

        font-family: Nunito Sans;
        font-style: normal;
        font-weight: 300;
        font-size: 12px;
        line-height: 16px;
        color: #9E9E9E;
    }
   
    .model-title-input-wrapper {
        // border-bottom: 1px solid #4D556A;
    }
    .model-title-input {
        margin: 0px 20px 0px;
        width: calc(100% - 40px);
        height: 40px;
        line-height: 40px;
        background: transparent;
        border: 1px solid #4D556A;
        box-sizing: border-box;
        border-radius: 2px;
        border-bottom: 1px solid #4D556A;
    }
    .main-actions-buttons {
        margin-top: auto;
        padding: 20px;

        display: flex;
        justify-content: space-between;
    }
    .action-button {
        height: 35px;
        width: 100%;

        background: #3F4C70;
        box-sizing: border-box;
        border-radius: 2px;
        box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.25);

        font-family: Nunito Sans;
        font-style: normal;
        font-weight: 600;
        font-size: 16px;
        line-height: 22px;

        text-align: center;

        color: #FFFFFF;
        &.is-disabled {
            // opacity: 0.3;
            background-color: rgb(120, 120, 120);
            cursor: not-allowed;
        }
    }
    .create-btn {
        background: #6185EE;
    }
    .mr-5 { margin-right: 5px;}
    .ml-5 { margin-left: 5px;}
    .template-image {
        margin-top: 10px;
        width: 50%;
        height: 50%;
        margin: 0 auto;

        svg { 
            display: block;
        }
    }
    .template-name {
        font-family: Nunito Sans;
        font-weight: 300;
        font-size: 12px;
        line-height: 16px;
        color: #C4C4C4;
        text-align: center;
    }
    .close-cross {
        position: absolute;
        right: 10px;
        top: 9px;
        width: 18px;
        height: 18px;
        cursor: pointer;
        &:after {
            content: '';
            position: absolute;
            width: 12px;
            height: 2px;
            background-color: #6185EE;
            left: 50%;
            top: 50%;
            transform-origin: 50% 50%;
            transform: translate(-50%, -50%) rotate(45deg);
        }
        &:before {
            content: '';
            position: absolute;
            width: 12px;
            height: 2px;
            background-color: #6185EE;
            left: 50%;
            top: 50%;
            transform-origin: 50% 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
        }
    }
    .plus-icon {
        vertical-align: sub;
        margin-right: 5px;
    }
    .template-description {
        margin: 0px 20px 40px;
        font-family: Nunito Sans;
        font-style: normal;
        font-size: 12px;
        line-height: 16px;
        min-height: 15rem;
        height: 16rem;
        font-weight: normal;
        line-height: 16px;
        color: #C4C4C4;        
    }
    .screenshoot-container {
        margin: 0 20px;
        margin-bottom: 20px;
        background: #23252A;
    }
    .template-description-else {
        min-height: 15rem;
    }
    .mode-path-wrapper {
        padding: 0 20px;
    }
</style>

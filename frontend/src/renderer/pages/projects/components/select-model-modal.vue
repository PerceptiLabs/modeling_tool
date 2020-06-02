<template lang="pug">
    div.select-model-modal
        .header 
            .close-cross(@click="closeModal()")
            span New Model
        .main-wrapper
            .main-templates
                .main-templates-header
                    h3 Templates
                    //- div.search-tempalte
                    //-     img(src="./../../../../../static/img/search-models.svg")
                    //-     input(type='text' placeholder="Search")
                .main-templates-items
                    .template-item(
                            :class="{'is-selected': (chosenTemplate === -1)}"
                            @click="choseTemplate(-1)"
                        )
                            div.template-image
                            span.template-name Empty
                    .template-item(
                        v-for="(temp, i) in basicTemplates"
                        :class="{'is-selected': (chosenTemplate === i)}"
                        @click="choseTemplate(i)"
                    )
                        div.template-image
                            img(v-if="temp.imgPath" :src="temp.imgPath" alt="classification")
                        span.template-name {{ temp.title }}
                    
            .main-actions 
                div  
                    h4.presets-text Name:
                    .model-title-input-wrapper
                        input.model-title-input(type="text" v-model="modelName")
                    h4.presets-text Model Path
                    .model-title-input-wrapper
                        input.model-title-input(type="text" v-model="modelPath" @click="openFilePicker")
                    p.template-description(v-if="chosenTemplate !== null") {{basicTemplates[chosenTemplate] &&basicTemplates[chosenTemplate].description}}
                .main-actions-buttons
                    button.action-button.mr-5(@click="closeModal()") Cancel
                    button.action-button.create-btn.ml-5(
                        :class="{'is-disabled': isDisableCreateAction()}"
                        @click="createModel()"
                    )
                        svg.plus-icon(width='17' height='17' viewbox='0 0 17 17' fill='none' xmlns='http://www.w3.org/2000/svg')
                            path(d='M11.7924 8.82157H8.96839V11.6386H8.0387V8.82157H5.22168V7.88489H8.0387V5.06787H8.96839V7.88489H11.7924V8.82157Z' fill='white')
                            rect(x='0.5' y='0.5' width='16' height='16' rx='1.5' stroke='white')
                        | Create
        file-picker-popup(
            v-if="showFilePickerPopup"
            popupTitle="Choose Model path"
            :startupFolder="this.modelPath"
            :confirmCallback="updateModelPath"
            :cancelCallback="closePopup"
        )
</template>
<script>
    import imageClassification    from '@/core/basic-template/image-classification.js'
    import reinforcementLearning  from '@/core/basic-template/reinforcement-learning.js'
    import timeseriesRegression   from '@/core/basic-template/timeseries-regression.js'
    import objectDetection        from '@/core/basic-template/object-detection.js'
    import ganTemplate            from '@/core/basic-template/gan-template.js'
    import FilePickerPopup        from "@/components/global-popups/file-picker-popup.vue";

    import { mapActions, mapState, mapGetters } from 'vuex';
    import { generateID } from '@/core/helpers';
    import cloneDeep from 'lodash.clonedeep';
export default {
    name: 'SelectModelModal',
    components: { FilePickerPopup },
    data: function() {
        return {
        basicTemplates: [
          {
            title: 'Image Classification',
            imgPath: './static/img/project-page/image-classification.svg',
            template: imageClassification,
            description: 'This is a simple image classification template, perfect for datasets such as Mnist. The standard dataset included with this template is a Mnist dataset where the input is an array of 784 grayscale pixel values and there are 10 unique label values (integers 0-9). The model consists of a reshaping component, a convolutional layer as well as a fully connected output layer with 10 neurons. Because of the reshaping component it requries the input data to be 784 or a form thereof (28x28 for example). The labels have to be an integer ranging from 0 to 9 to be compatable with the one hot encoding being applied to the labels.'
          },
          {
            title: 'Timeseries Regression',
            imgPath: './static/img/project-page/time-series-regression.svg',
            template: timeseriesRegression,
            description: `This is a template for linear regression, where it tries to create a line of best fit for the datapoints you load. The standard dataset is a one dimensional input value and one dimensional labels. The input data can be multidimensional, but our visualizations only allow for one dimensional data at the moment. The labels data can only be one dimensional as they represent the value of the input data. The model is built as a single fully connected layer with one neuron as output.`
          },
          {
            title: 'Reinforcement Learning',
            imgPath: './static/img/project-page/reinforcement-learning.svg',
            template: reinforcementLearning,
            description: `The is a template for Reinforcement Learning consisting of one grayscale component, one convolutional layer and one fully connected layer as output. This template uses Q learning on Atari Gym games, where it is set up to play breakout. To play another game, make sure that you change the neurons from the fully connected layer to match the number of possible actions in the actionspace, which you can see in the Environment component.`
          },
           {
            title: 'Object Detection',
            imgPath: '',
            template: objectDetection,
            description: `This is a template of the Object Detection model YOLO. It trains on a custom built dataset containing different shapes as standard. Since it consists of only convolutional layers, any input data will work to train on, just make sure that the label data matches the input data properly.`
          },
          {
            title: 'GAN',
            imgPath: '',
            template: ganTemplate,
            description: `This is a template for a Generative Adversarial Network (GAN) where it trains on the Mnist data as a standard. The model consists of a generative network and a discriminative network, as well as a switch layer layer which switches between the generated image and real image.`
          },
        ],
        chosenTemplate: null,
        modelName: '',
        description: '',
        modelPath: '',
        showFilePickerPopup: false,
    }
    },
    computed: {
        ...mapState({
          currentProjectId: state => state.mod_project.currentProject,  
        }),
        ...mapGetters({
            currentProject: 'mod_project/GET_project',
            projectPath: 'mod_project/GET_projectPath'
        })
    },
    mounted() {
        this.modelPath = this.projectPath;
    },
    methods: {
        ...mapActions({
            addNetwork:                 'mod_workspace/ADD_network',
            createProjectModel:         'mod_project/createProjectModel',
            getModelMeta:               'mod_project/getModel',
            showErrorPopup:             'globalView/GP_errorPopup',
            isDirExists:                'mod_api/API_isDirExist',
        }),
        closeModal() {
            this.$emit('close');
        },
        choseTemplate(index) {
            this.chosenTemplate = index;
        },
        isDisableCreateAction() {
            const { chosenTemplate, modelName, basicTemplates } = this;
            return ((chosenTemplate === null) || !modelName);
        },
        async createModel() {
            const { chosenTemplate, modelName, basicTemplates } = this;
            if((chosenTemplate === null) || !modelName)  return


            // check if models name already exists
            const promiseArray = 
                this.currentProject.models
                    .map(x => this.getModelMeta(x));
            const modelMeta = await Promise.all(promiseArray);
            const modelNames = modelMeta.map(x => x.name);
            if(modelNames.indexOf(modelName) !== -1) {
                this.showErrorPopup(`The name of model "${modelName}" already exists.`);
                return;
            }
            
            const dirAlreadyExist = await this.isDirExists(`${this.modelPath}/${modelName}`);
            if(dirAlreadyExist) {
                this.showErrorPopup(`The "${modelName}" folder already exists in "${this.modelPath}" location.`);
                return;
            }

            let modelType;

            this.createProjectModel({
                name: modelName,
                project: this.currentProjectId,
                location: `${this.modelPath}/${modelName}`,
            }).then(apiMeta => {
                if(chosenTemplate === -1) {
                    this.addNetwork({ apiMeta });
                    modelType = 'Custom';

                } else {
                    let template = cloneDeep(basicTemplates[chosenTemplate].template.network);
                    template.networkName = modelName;
                    template.networkID = apiMeta.model_id;
                    this.addNetwork({network: template, apiMeta});
                    
                    modelType = basicTemplates[chosenTemplate].title;
                }
            });
            
            this.$store.dispatch('mod_tracker/EVENT_modelCreation', modelType, {root: true});

            this.closeModal();

        },
        openFilePicker() {
            this.showFilePickerPopup = true;
        },
        setPath(data) {
            console.log(data);
            debugger;
        },
        closePopup() {
            this.showFilePickerPopup = false;
        },
        updateModelPath(filepath) {
            this.modelPath = filepath && filepath[0] ? filepath[0] : '';
            this.showFilePickerPopup = false;
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
    .header {
        position: relative;
        height: 38px;
        display: flex;
        justify-content: center;
        align-items: center;
        
        background: rgba(97, 133, 238, 0.2);
        border: 1px solid rgba(97, 133, 238, 0.4);
        border-radius: 2px 2px 0px 0px;

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
        .search-tempalte {
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

        background: rgba(97, 133, 238, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-sizing: border-box;
        border-radius: 2px;

        font-family: Nunito Sans;
        font-style: normal;
        font-weight: 600;
        font-size: 16px;
        line-height: 22px;

        text-align: center;

        color: #FFFFFF;
        &.is-disabled {
            opacity: 0.3;
            background-color: #ccc;
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
        padding: 30px 20px 0;
        font-family: Nunito Sans;
        font-style: normal;
        font-weight: 300;
        font-size: 12px;
        line-height: 16px;
        color: #9E9E9E;
    }
</style>
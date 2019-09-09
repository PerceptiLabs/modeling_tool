import { isNumber } from "util";
import router from "@/router";
import store  from '@/store'

const namespaced = true;
let delayTimer;

const state = {
  isTutorialMode: false,
  showTutorialStoryBoard: false,
  showMainTutorialInstruction: false,
  mainTutorialIsStarted: false,
  interactiveInfo: false,
  isDottedArrow: false,
  
  activeStepStoryboard: 0,
  
  activeStepMainTutorial: 0,
  activePointMainTutorial: 0,
  activeActionMainTutorial: 0,
  
  //firstTimeApp: localStorage.showFirstAppTutorial ? false : true,
  interective: {
    first_instructions: {
      title: 'Instructions:',
      points: [
        {
          actions: [
            {
              tooltip: '',
              actionStatus: 'first'
            },
          ],
          status:'first',
          content: `<div class="text-block">When working with AI, you can divide the process into 2 overarching steps:</div>
                    <p>1) Knowing your data</p>
                    <p>2) Building your model</p>`
        }
      ]
    },
    import_data: {
      title: 'Step 1. Import your data',
      points: [
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: `In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Data</div> > Select and drop <div class="marker">Data</div> to workspace > Load dataset`,
          actions: [
            {
              tooltip: 'Click to Data',
              position: 'right',
              id: 'tutorial_data',
              status: 'disabled'
            },
            {
              tooltip: 'Drag & drop Data',
              position: 'right',
              id: 'tutorial_data-data',
              dynamic_id: 'tutorial_data-data-1',
              schematic: {
                type: 'square',
                top: 16.4,
                left: 26
              },
              status: 'disabled'
            },
            {
              tooltip: `Double click for select <br> MNIST dataset`,
              position: 'right',
              id: 'tutorial_data-data-1',
              status: 'disabled',
              position_element: {
                top: 6.5,
                left: 18
              },
            },
            {
              tooltip: `Click for select and <br> load mnist_input.npy`,
              position: 'right',
              id: 'tutorial_button-load',
              status: 'disabled'
            },
            {
              tooltip: 'Click to Apply loaded MNIST',
              position: 'right',
              id: 'tutorial_button-apply',
              status: 'disabled'
            },
            {
              tooltip: 'Click to confirm',
              position: 'right',
              id: 'tutorial_button-confirm',
              status: 'disabled'
            }
          ],
          static_info: [
            {
              status:'disabled',
              content: 'For this tutorial we will use the MNIST dataset'
            },
            {
              status:'disabled',
              content: 'Every input image inside the mnist_input.npy file'
            }
          ]
        },
        {
          status:'disabled',
          content: 'Repeat this step for your label data – also known as ground truth (GT) required to train your supervised AI model.',
          actions: [
            {
              tooltip: 'Click to Data',
              position: 'right',
              id: 'tutorial_data',
              status: 'disabled'
            },
            {
              tooltip: 'Drag & drop Data',
              position: 'right',
              id: 'tutorial_data-data',
              dynamic_id: 'tutorial_data-data-2',
              schematic: {
                type: 'square',
                top: 32.4,
                left: 26
              },
              status: 'disabled'
            },
            {
              tooltip: `Double click for select <br> MNIST dataset`,
              position: 'right',
              id: 'tutorial_data-data-2',
              status: 'disabled',
            },
            {
              tooltip: `Click for select and <br> load mnist_labels.npy`,
              position: 'right',
              id: 'tutorial_button-load',
              status: 'disabled'
            },
            {
              tooltip: 'Click to Apply loaded MNIST',
              position: 'right',
              id: 'tutorial_button-apply',
              status: 'disabled'
            },
            {
              tooltip: 'Click to confirm',
              position: 'right',
              id: 'tutorial_button-confirm',
              status: 'disabled'
            }
          ],
        }
      ]
    },
    precessing_reshape: {
      title: 'Step 2. Reshape the dataset',
      points: [
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Processing</div> > Connect input > Operation settings  ',
          actions: [
            {
              tooltip: 'Click to Processing',
              position: 'right',
              id: 'tutorial_processing',
              status: 'disabled'
            },
            {
              tooltip: 'Drag & drop Reshape',
              position: 'right',
              id: 'tutorial_process-reshape',
              dynamic_id: 'tutorial_process-reshape-1',
              schematic: {
                type: 'square',
                top: 16.4,
                left: 42,
              },
              status: 'disabled'
            },
            {
              tooltip: 'Click to create a connection',
              position: 'right',
              id: 'tutorial_list-arrow',
              status: 'disabled',
              check_prev_id: true
            },
            {
              tooltip: `Connect Data with <br> Process Reshape`,
              position: 'right',
              id: 'tutorial_process-reshape-1',
              schematic: {
                type: 'arrow',
                connection_start: 'tutorial_data-data-1',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Click to go back to work with items',
              position: 'right',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Double click to open settings',
              position: 'right',
              id: 'tutorial_process-reshape-1',
              status: 'disabled'
            }
          ],
          static_info: [
            {
              status:'disabled',
              content: 'We want to build an image classifier by using images as input, not a flattened array'
            },
          ]
        },
        {
          status:'disabled',
          content: 'Reshape the dataset into images of shape 28x28x1. ',
          hoverInfo: [
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Reshape to 28x28x1 and
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_input-reshape',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Axis positions of the data
                          <div class="tooltip-tutorial_bold">click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_input-transpose',
            }
          ],
          actions: [
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Reshape to 28x28x1 and
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_input-reshape',
              status: 'disabled'
            }
          ],
        },
      ]
    },
    convolutional_layer: {
      title: 'Step 3. Use a Convolutional layer',
      points: [
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Deep Learning</div> > <div class="marker">Convolution</div> > Connect input > Operation settings',
          hoverInfo: [
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Dimension</div>
                          Choose which type of convolutional operation to use
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_dimension',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Patch size:</div> 
                          This is the size of the filter.</br> 
                          E.g. with patch size 3, the </br> 
                          filter will be a square of size 3x3. </br> 
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_patch-size',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Stride:</div>
                          This is the step size when </br>
                          we slide the filter over the input </br>
                          data to generate feature maps. </br>
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_stride'
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Feature Maps:</div>
                          The number of </br>
                          feature maps correspond to the </br>
                          number of different features to </br>
                          look for in the input data. i.e. with </br>
                          more complex data, it might be </br>
                          better to increase the number </br>
                          of feature maps. </br>
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_feature-maps',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Zero-padding</div>
                          Choose if Zero-padding should be used or not
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_zero-padding',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Activation function</div>
                          Choose which activation function to use
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_activeFunc',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Dropout</div>
                          Choose if dropout should be used or not
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_dropout',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Pooling</div>
                          Choose if pooling should be used or not
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_pooling',
            }
          ],
          actions: [
            {
              tooltip: 'Click to Deep Learning',
              position: 'right',
              id: 'tutorial_deep-learning', 
              status: 'disabled'
            },
            {
              tooltip: 'Drag & drop Convolution',
              position: 'right',
              id: 'tutorial_convolution',
              dynamic_id: 'tutorial_convolution-1',
              schematic: {
                type: 'square',
                top: 16.4,
                left: 58,
              },
              status: 'disabled'
            },
            {
              tooltip: 'Click to create a connection',
              position: 'right',
              id: 'tutorial_list-arrow',
              status: 'disabled',
              check_prev_id: true
            },
            {
              tooltip: 'Connect Process Reshape <br> with Deep learning convolution',
              position: 'right',
              id: 'tutorial_convolution-1',
              schematic: {
                type: 'arrow',
                connection_start: 'tutorial_process-reshape-1',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Click to go back to work with items',
              position: 'right',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Double click to open settings',
              position: 'right',
              id: 'tutorial_convolution-1',
              status: 'disabled'
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Patch size:</div> 
                          This is the size of the filter.</br> 
                          E.g. with patch size 3, the </br> 
                          filter will be a square of size 3x3. </br> 
                         <div class="tooltip-tutorial_bold">Hover on next input to see more information</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_patch-size',
              status: 'disabled'
            },
          ],
          static_info: [
            {
              status:'disabled',
              content: 'Convolution means to slide several filters over the input data.',
            },
            {
              status:'disabled',
              content: 'This generates outputs called feature maps, where each feature map corresponds to an extracted feature.'
            }
          ]
        },
      ]
    },
    fully_connected_layer: {
      title: 'Step 4. Use a Fully Connected layer',
      points: [
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Deep Learning</div> > <div class="marker">Fully Connected</div> > Connect input > Set neurons',
          actions: [
            {
              tooltip: 'Click to Deep Learning',
              position: 'right',
              id: 'tutorial_deep-learning', 
              status: 'disabled'
            },
            {
              tooltip: 'Drag & drop Fully Connected',
              position: 'right',
              id: 'tutorial_fully-connected',
              dynamic_id: 'tutorial_fully-connected-1',
              schematic: {
                type: 'square',
                top: 16.4,
                left: 74,
              },
              status: 'disabled'
            },
            {
              tooltip: 'Click to create a connection',
              position: 'right',
              id: 'tutorial_list-arrow',
              status: 'disabled',
              check_prev_id: true
            },
            {
              tooltip: 'Connect Deep Learning Conv <br> with Deep learning FC',
              position: 'right',
              id: 'tutorial_fully-connected-1',
              schematic: {
                type: 'arrow',
                connection_start: 'tutorial_convolution-1',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Click to go back to work with items',
              position: 'right',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Double click to open settings',
              position: 'right',
              id: 'tutorial_fully-connected-1',
              status: 'disabled'
            }
          ],
          static_info: [
            {
              status:'disabled',
              content: 'This operation matches the size of outputs of your model to the number of classes from your label data',
            }
          ]
        },
        {
          status:'disabled',
          content: 'Set the same number of neurons as there are classes, which in this case is 10 since the images represent digits 0-9. ',
          hoverInfo: [
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Set how many neurons to use
                          <div class="tooltip-tutorial_bold">Hover on next input to see <br> more information and click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_neurons',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                         Choose activation function for each neuron
                          <div class="tooltip-tutorial_bold">Hover on next input to see <br> more information and click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_activation_function',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Choose if dropout should be used or not
                          <div class="tooltip-tutorial_bold">click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_dropout',
            }
          ],
          actions: [
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Set how many neurons to use
                          <div class="tooltip-tutorial_bold">Hover on next input to see <br> more information and click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_neurons',
              status: 'disabled'
            },
          ],
        },
      ]
    },
    one_hot_encoding: {
      title: 'Step 5. One Hot encoding on labels',
      points: [
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Processing</div> > <div class="marker">One Hot</div> > Connect input > Set classes',
          actions: [
            {
              tooltip: 'Click to Processing',
              position: 'right',
              id: 'tutorial_processing', 
              status: 'disabled'
            },
            {
              tooltip: 'Drag & drop One Hot',
              position: 'right',
              id: 'tutorial_one-hot',
              dynamic_id: 'tutorial_one-hot-1',
              schematic: {
                type: 'square',
                top: 32.4,
                left: 42,
              },
              status: 'disabled'
            },
            {
              tooltip: 'Click to create a connection',
              position: 'right',
              id: 'tutorial_list-arrow',
              status: 'disabled',
              check_prev_id: true
            },
            {
              tooltip: 'Connect Data with Process One Hot',
              position: 'right',
              id: 'tutorial_one-hot-1',
              schematic: {
                type: 'arrow',
                connection_start: 'tutorial_data-data-2',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Click to go back to work with items',
              position: 'right',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Double click to set classes',
              position: 'right',
              id: 'tutorial_one-hot-1',
              status: 'disabled'
            },
            {
              tooltip: 'Set 10 and click Apply changes',
              position: 'right',
              id: 'tutorial_number-of-classes',
              status: 'disabled'
            }
          ],
          static_info: [
            {
              status:'disabled',
              content: 'This operation transforms your label data to one dimension for each digit/ class (i.e. 10, in this case). '
            },
            {
              status:'disabled',
              content: 'This makes it easier for the AI to differentiate the digits so it can learn faster. '
            }
          ]
        },
      ]
    },
    train_normal: {
      title: 'Step 6. Train your AI model',
      points: [
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Training</div> > <div class="marker">Normal</div> > Connect input > Define parameters',
          hoverInfo: [
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Choose which input connection <br> is represent the labels
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_labels',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Choose in which position to <br> split at the chosen axis
                         <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_cost-function',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Choose which optimizer to use
                          <div class="tooltip-tutorial_bold">Hover on next input to see more <br> information and then click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_optimizer',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Set the learning rate
                          <div class="tooltip-tutorial_bold">click Apply</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_learning_rate',
            }
          ],
          actions: [
            {
              tooltip: 'Click to Training',
              position: 'right',
              id: 'tutorial_training', 
              status: 'disabled'
            },
            {
              tooltip: 'Drag & drop Normal',
              position: 'right',
              id: 'tutorial_training-normal',
              dynamic_id: 'tutorial_training-normal-1',
              schematic: {
                type: 'square',
                top: 32.4,
                left: 75,
              },
              status: 'disabled'
            },
            {
              tooltip: 'Click to create a connection',
              position: 'right',
              id: 'tutorial_list-arrow',
              status: 'disabled',
              check_prev_id: true
            },
            {
              tooltip: 'Connect Process one Hot with Train Normal',
              position: 'right',
              id: 'tutorial_training-normal-1',
              schematic: {
                type: 'arrow',
                connection_start: 'tutorial_one-hot-1',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Connect Deep learning FC with Train Normal',
              position: 'right',
              id: 'tutorial_training-normal-1',
              schematic: {
                type: 'arrow',
                position: 'bottom',
                connection_start: 'tutorial_fully-connected-1',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Click to go back to work with items',
              position: 'right',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Double click to define parameters',
              position: 'right',
              id: 'tutorial_training-normal-1',
              status: 'disabled'
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Cost function:</div> 
                          calculates the error </br> 
                          of the prediction, which is required </br> 
                          for backpropagation.
                       </div>`,
              position: 'right',
              id: 'tutorial_cost-function',
              status: 'disabled'
            }
          ],
          static_info: [
            {
              status:'disabled',
              content: 'Now that the size of output from the Fully Connected (FC) layer and One Hot layer match, the AI can compare its predictions from the FC layer and answers (GT) from the One Hot. '
            }
          ]
        },
      ]
    },
    run_training: {
      title: 'Step 7. Run training data',
      points: [
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: `In the <div class="marker">Top Toolbar</div> go to <div class="marker">Run</div>
                    Check all inputs in General Settings and click Apply`,
          hoverInfo: [
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Partition:</div> is the percentage of data </br> that goes into training, validation, </br> and testing respectively. </br>
                          <div class="tooltip-tutorial_bold">Hover on next input to see <br> more information and click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_partition-training-input',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Partition:</div> is the percentage of data </br> that goes into training, validation, </br> and testing respectively. </br>
                          <div class="tooltip-tutorial_bold">Hover on next input to see <br> more information and click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_partition-validation-input',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Partition:</div> is the percentage of data </br> that goes into training, validation, </br> and testing respectively. </br>
                          <div class="tooltip-tutorial_bold">Hover on next input to see <br> more information and click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_partition-test-input',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Batch size:</div> to make the training </br> more efficient, you can train on </br> multiples samples at the same time. </br>
                          <div class="tooltip-tutorial_bold">Hover on next input to see <br> more information and click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_butch-size-input',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Choose to shuffle the data or not
                          <div class="tooltip-tutorial_bold">Hover on next input to see <br> more information and click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_shuffle_data',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Epoch:</div> refers to the number of times </br> you want to run through your entire dataset. </br>
                          <div class="tooltip-tutorial_bold">Hover on next input to see <br> more information and click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_epochs-input',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Dropout rate:</div> when training we can </br> deactivate half (0.5) of all the </br> learning neurons in each layer in order for </br> the model to learn in a  more general way. 
                          </br></br> Note: this has to be activated independently </br> for each deep learning layer.</br>
                          <div class="tooltip-tutorial_bold">click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_drop-rate-input',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          Set how often to save a trained model
                          <div class="tooltip-tutorial_bold">click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_save_model_every',
            },
          ],
          actions: [
            {
              tooltip: 'Click to run training',
              position: 'bottom',
              id: 'tutorial_run-training-button', 
              status: 'disabled'
            },
/*            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Partition:</div> is the percentage of data </br> that goes into training, validation, </br> and testing respectively. </br>
                          <div class="tooltip-tutorial_bold">Hover on next input to see more information</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_partition-training-input',
              status: 'disabled'
            },*/
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Epoch:</div> refers to the number of times </br> you want to run through your entire dataset. </br>
                          <div class="tooltip-tutorial_bold">Hover on next input to see <br> more information and click Apply</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_epochs-input',
              status: 'disabled'
            },
          ]
        },
      ]
    },
    training: {
      title: 'Step 8. Training',
      points: [
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'The top window shows training <div class="marker">Statistics</div> for the overall model. Press <div class="marker">"Next"</div> to continue',
          actions: [
            {
              id: 'tutorial_statistics', 
              status: 'disabled',
              schematic: {
                type: 'border'
              },
              next: true
            }
          ]
        },
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'The <div class="marker">ViewBox</div> shows what’s happening in each component. Select any layer on the <div class="marker">Map View</div> to go into more detail. Press <div class="marker">"Next"</div> to continue',
          actions: [
            {
              id: 'tutorial_view-box', 
              status: 'disabled',
              schematic: {
                type: 'border',
              },
              next: true
            }
          ]
        },
/*        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'The <div class="marker">Pause</div> to learn  further details',
          actions: [
            {
              tooltip: 'Click to pause',
              position: 'bottom',
              id: 'tutorial_pause-training',
              status: 'disabled',
            }
          ]
        },*/
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'Click <div class="marker">Reshape</div> in the <div class="marker">Map View</div> </br> Notice the corresponding display in the <div class="marker">ViewBox</div>',
          actions: [
            { 
              tooltip: 'Click Reshape',
              position: 'right',
              id: 'tutorial_process-reshape-1',
              status: 'disabled',
            }
          ]
        },
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'Click <div class="marker">Fully Connected (FC)</div> in the <div class="marker">Map View</div> See that the output line in FC is the same as <div class="marker">ViewBox</div> Press <div class="marker">"Next"</div> to continue',
          actions: [
            { 
              tooltip: 'This is the image that <br/> the AI trying to classify. </br> Press"Next" to continue',
              position: 'right',
              id: 'tutorial_view-box',
              status: 'disabled',
              next: true
            },
            { 
              tooltip: 'Click Fully Connected',
              position: 'right',
              id: 'tutorial_fully-connected-1',
              status: 'disabled',
            },
            { 
              id: 'tutorial_prediction-chart',
              position: 'right',
              status: 'disabled',
              schematic: {
                type: 'border',
              },
              next: true
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Click to Prediction:</div> Overview of the </br> model perfomance
                        </div>`,
              position: 'right',
              id: 'tutorial_prediction-tab',
              status: 'disabled',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Click to Accuracy:</div> Overall </br> performance of a model. </br> The higher the accuracy, </br> the better it is at learning. 
                        </div>`,
              position: 'right',
              id: 'tutorial_accuracy-tab',
              status: 'disabled',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Click to Loss:</div> How much error there is in your predictions.
                        </div>`,
              position: 'right',
              id: 'tutorial_loss-tab',
              status: 'disabled',
            }
          ]
        },
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'Continue training.',
          actions: [
            {
              tooltip: 'Click to unpause',
              position: 'bottom',
              id: 'tutorial_pause-training',
              status: 'disabled',
            }
          ]
        },
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'Wait until training is complete for this model.',
          actions: [
            {
              position: 'right',
              status: 'disabled',
              id:'tutorial_statistic-tab'
            }
          ]
        },
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'Click to start test',
          actions: [
            {
              tooltip: 'Click to start test',
              position: 'right',
              status: 'disabled',
              id:'tutorial_run-test-button'
            }
          ]
        },
      ]
    },
    testing: {
      title: 'Step 9. Testing shows how general your model is, i.e. to what extent can it classify things it has never seen before',
      points: [
        {
          status:'last step',
          class_style: 'list_subtitle',
          content: 'Testing shows how general your model is, i.e. to what extent can it classify things it has never seen before',
          actions: [
            {
              tooltip: 'Click to explore view controls',
              position: 'right',
              status: 'disabled',
              id:'tutorial_play-test-button'
            }
          ]
        }
      ]
    },
/*    save_and_export: {
      title: `Step 10.`,
      points: [
        {
          content:`You have now finished training a model and the tutorial is done. 
                  If you wish to save the model you can do so from the File menu in the top left. 
                  Or you can export it by clicking on the tab "Export" in the right menu.`,
          status:'last step',
          actions: [
            {
              status: 'disabled',
            }
          ]
        }
      ]
    }*/
  }
};

const getters = {
  getActiveStepStoryboard(state) {
    return state.activeStepStoryboard;
  },
  getIterective(state) {
    return state.interective
  },
  getIsTutorialStoryBoard(state) {
    return state.showTutorialStoryBoard
  },
  getIstutorialMode(state) {
    return state.isTutorialMode
  },
  getShowMainTutorialInstruction(state) {
    return state.showMainTutorialInstruction
  },
  getInteractiveInfo(state) {
    return state.interactiveInfo
  },
  getMainTutorialIsStarted(state) {
    return state.mainTutorialIsStarted
  },
  getActiveStepMainTutorial(state) {
    return state.activeStepMainTutorial
  },
  getActivePointMainTutorial(state) {
    return state.activePointMainTutorial
  },
  getActiveActionMainTutorial(state) {
    return state.activeActionMainTutorial
  },
  getActiveStep(state) {
    return Object.keys(state.interective)[state.activeStepMainTutorial]
  },
  getPoints(state, getters) {
    return state.interective[getters.getActiveStep].points
  },
  getActivePoint(state, getters) {
    return getters.getPoints[state.activePointMainTutorial]
  },
  getActiveAction(state, getters) {
    return getters.getActivePoint ? getters.getActivePoint.actions[state.activeActionMainTutorial] : '';
  },
  getPrevActiveAction(state, getters) {
    return getters.getActivePoint ? getters.getActivePoint.actions[state.activeActionMainTutorial - 1] : '';
  },
  getAllPointsIsDone(state, getters) {
    var count = 0;
    getters.getPoints.forEach(point => {
      if(point.status === 'done') count++
    });
    return count === getters.getPoints.length
  },
  getHoverInfo(state, getters) {
    return  getters.getActivePoint.hoverInfo;
  },
  getIsDottedArrow(state) {
    return  state.isDottedArrow;
  }
};

const mutations = {
  SET_isTutorialMode(state, value) {
    state.isTutorialMode = value
  },
  SET_mainTutorialIsStarted(state, value) {
    state.mainTutorialIsStarted = value
  },
  SET_runButtonsActive(state, value) {
    state.runButtonsActive = value;
  },
  SET_activeStepStoryboard(state, value) {
    switch(value) {
      case 'next':
        state.activeStepStoryboard++;
        break;
      case 'prev':
        state.activeStepStoryboard--;
        break;
      default:
        state.activeStepStoryboard = value;
        break;
    }
  },
  SET_showTutorialStoryBoard(state, value) {
    state.showTutorialStoryBoard = value;
    //state.firstTimeApp = value;
  },
  SET_showMainTutorialInstruction(state, value) {
    state.showMainTutorialInstruction = value
  },
  SET_activeStepMainTutorial(state, value) {
    if(isNumber(value)) {
      state.activeStepMainTutorial = value
    } else if(value === 'next') {
      state.activeStepMainTutorial++
    }
  },
  SET_activePointMainTutorial(state, value) {
    if(isNumber(value)) {
      state.activePointMainTutorial = value
    } else if(value === 'next') {
      state.activePointMainTutorial++
    }
  },
  SET_interactiveInfo(state, value) {
    state.interactiveInfo = value;
  },
  SET_staticInfoValue(state, value) {
    let static_info = state.interective[value.step].points[value.point].static_info;
    static_info[value.index].status = value.status
  },
  SET_activeActionMainTutorial(state, value) {
    if(isNumber(value)) {
      state.activeActionMainTutorial = value
    }
    else if(value === 'next') {
      state.activeActionMainTutorial++
    }
    else if(value === 'prev') {
      state.activeActionMainTutorial--
    }
  },
  SET_pointActivate(state, value,) {
    let points = state.interective[value.step].points;
    points[value.point].status = value.status;

  },
  SET_activeAction(state, value) {
    let actions = state.interective[value.step].points[value.point].actions;
    actions[value.action].status = value.status
  },
  SET_isDottedArrow(state, value) {
    state.isDottedArrow = value;
}
};

const actions = {
  pointActivate({commit, dispatch, getters}, value) {
    if(getters.getIstutorialMode && 
      getters.getMainTutorialIsStarted && 
      getters.getActiveAction && 
      getters.getActiveAction.id === value.validation) {
        if(value.way === 'next')  {
          dispatch('removeDuplicateId');
          dispatch('checkActiveActionAndPoint', value);
          if(getters.getActivePoint) dispatch('unlockElement', getters.getActiveAction.id);
        }
        else {
          dispatch('removePrevUnlock');
          if(getters.getActivePoint) dispatch('unlockElement', getters.getActiveAction.id);
          dispatch('createTooltip', {id: getters.getActiveAction.id, tooltip: getters.getActiveAction.tooltip});
          dispatch('drawSchematicElement', getters.getActiveAction.schematic);
          commit('SET_pointActivate', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, status: 'active'});
        }
    }
  },
  checkActiveActionAndPoint({commit, dispatch, getters}, value) {
    commit('SET_activeAction', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, action: getters.getActiveActionMainTutorial, status: 'done'});
    commit('SET_activeActionMainTutorial', 'next');
    if(getters.getActiveAction) {
      let checkId = document.getElementById(getters.getActiveAction.id);
      let prevId = getters.getActiveAction.check_prev_id;
      if(prevId) checkId = document.getElementById(getters.getPrevActiveAction.dynamic_id);
      if(!checkId) {
        commit('SET_activeActionMainTutorial', 'prev');
      }
      dispatch('createTooltip', {id: getters.getActiveAction.id, tooltip: getters.getActiveAction.tooltip});
      dispatch('removeSchematicElement');
      dispatch('drawSchematicElement', getters.getActiveAction.schematic);
      dispatch('showHoverInfo');
    } 
    else { // all actions has been done
      dispatch('removeTooltip');
      dispatch('nextPoint');
      if(getters.getActivePoint) {
        commit('SET_pointActivate', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, status: 'active'});
        dispatch('createTooltip', {id: getters.getActiveAction.id, tooltip: getters.getActiveAction.tooltip});
      }
      else { //all points has been done
        dispatch('removeTooltip');
        commit('SET_activePointMainTutorial', 0);
        dispatch('lockOneElement');
      }
    }
  },
  createTooltip({getters, dispatch}, info) {
    dispatch('removeTooltip');
    let element = document.getElementById(info.id);
    if(getters.getActiveAction.tooltip && element) {
      var tooltip = document.createElement('div');
      delayTimer = setTimeout(()=>{
        dispatch('sideCalculate', {element, tooltip, side: getters.getActiveAction.position});
        tooltip.classList.add('tooltip-tutorial', `tooltip-tutorial--${getters.getActiveAction.position}`);
        tooltip.innerHTML = info.tooltip;
        document.body.appendChild(tooltip);
        element.addEventListener('mouseup', repositionElement);
      }, 250);
    }
    function repositionElement() {
      dispatch('sideCalculate', {element, tooltip, side: getters.getActiveAction.position});
    }
  },
  removeTooltip() {
    let activeTooltips = document.querySelectorAll('.tooltip-tutorial');
    clearTimeout(delayTimer);
    if(activeTooltips.length > 0){
      activeTooltips.forEach((tooltip)=> {
        tooltip.remove();
      })
    }
  },
  showHideTooltip({getters}) {
    if(getters.getIstutorialMode) {
      let element = document.getElementById(getters.getActiveAction.id);
      if(element.parentNode.classList.contains('unlock-element')) {
        let activeTooltip = document.querySelector('.tooltip-tutorial');
        activeTooltip.classList.contains('tooltip-hide') ?
          activeTooltip.classList.remove('tooltip-hide') : activeTooltip.classList.add('tooltip-hide')
      }
    }
  },
  hideTooltip({getters}) {
    let element = document.getElementById(getters.getActiveAction.id);
    if(element && element.parentNode.classList.contains('unlock-element')) {
      document.querySelector('.tooltip-tutorial').classList.add('tooltip-hide');
    }
  },
  nextPoint({commit, getters, dispatch}) {
    commit('SET_activeActionMainTutorial', 0);
    commit('SET_pointActivate', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, status: 'done'});
    let static_info = getters.getActivePoint.static_info;
    if(static_info) {
      for(let i = 0; i < static_info.length; i++ ) {
        commit('SET_staticInfoValue', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, index: i, status: 'done'})
      }
    }
    commit('SET_activePointMainTutorial', 'next');
    dispatch('drawSchematicElement', getters.getActiveAction.schematic)
  },
  drawSchematicElement({getters, commit}, schematic) {
    let tutorial_targetBorder = document.querySelector('.tutorial_target-border');
    if(tutorial_targetBorder) tutorial_targetBorder.classList.remove('tutorial_target-border');
    if(schematic) {
      switch (schematic.type) {
        case 'square':
          let infoSection = document.querySelector('.info-section_main');
          let element = document.createElement('div');
          element.classList.add('schematic');
          infoSection.insertBefore(element, infoSection.firstChild);
          element.classList.add('schematic--square');
          element.style.top = schematic.top + 'rem';
          element.style.left = schematic.left + 'rem';
          break;
        case 'border':
         let domElement = document.getElementById(getters.getActiveAction.id);
         domElement.classList.add('tutorial_target-border');
         break;
        case 'arrow':
          commit('SET_isDottedArrow', true);
          let arrowSize = 10;
          let firstElement = document.getElementById(getters.getActiveAction.schematic.connection_start);
          let secondElement = document.getElementById(getters.getActiveAction.id);

          let start = firstElement.getBoundingClientRect();
          let stop = secondElement.getBoundingClientRect();

          if(getters.getActiveAction.schematic.position === 'bottom') {
            store.commit('mod_workspace/SET_preArrowStart', {x: start.right - start.width - start.width / 2 - arrowSize, y: start.top - start.width});
            store.commit('mod_workspace/SET_preArrowStop', {x: stop.right - start.width - start.width / 2 - arrowSize, y: stop.top - start.width*2 + arrowSize});
          }
          else {
            store.commit('mod_workspace/SET_preArrowStart', {x: start.right - start.width - arrowSize, y: start.top - start.height - arrowSize});
            store.commit('mod_workspace/SET_preArrowStop', {x: stop.right -  stop.width*2 - arrowSize, y: stop.top - stop.height - arrowSize});
          }
      }
    }
  },
  showHoverInfo({getters, dispatch}) { //main tutorial hover tooltips
    setTimeout(()=> {
      const elements = document.querySelectorAll('[data-tutorial-hover-info]');
      if(elements.length > 0) {
        elements.forEach(function (element, index) {
          element.addEventListener('mouseenter', function (event) {
            dispatch('createTooltip', {id: getters.getHoverInfo[index].id, tooltip: getters.getHoverInfo[index].tooltip});
          });
          element.addEventListener('mouseleave', function (event) {
            dispatch('removeTooltip');
          })
        })
      }
    }, 3000)
  },
  lockElements({getters, dispatch}, cssSelector) {
    let elements = document.querySelectorAll(cssSelector);
    let blockingArea = document.createElement('div');
    blockingArea.classList.add('lock-area');
    elements.forEach(function (element) {
      element.appendChild(blockingArea.cloneNode(true));
    });
  },
  unlockElement({getters, dispatch}, id) {
    let element = document.getElementById(id);
    if(element && element.parentNode.parentNode.classList.contains('layersbar-list') ||
      element && element.parentNode.parentNode.classList.contains('layer_child-list')) {
        element.parentNode.classList.add('unlock-element')
    }
  },
  unlockAllElements() {
    let lockElements = document.querySelectorAll('.lock-area');
    if(lockElements.length > 0) {
      lockElements.forEach(function (element) {
        element.remove();
      })
    }
  },
  removePrevUnlock() {
    let prevUnlockElements = document.querySelectorAll('.unlock-element');
    if(prevUnlockElements.length > 0) {
      prevUnlockElements.forEach(function (element) {
        element.classList.remove('unlock-element');
      })
    }
  },
  lockOneElement() {
    setTimeout(()=> {
      let element = document.querySelector('.unlock-element');
      if(element) element.classList.remove('unlock-element');
    }, 100);
  },
  sideCalculate({rootGetters}, info) {
   if(info.element) {
     let elCoord = info.element.getBoundingClientRect();
     let tooltipArrow = 10;
     let isDraggable = info.element.getAttribute('draggable');
     let zoom = isDraggable !== 'false' ? 1 : store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom;
     switch (info.side) {
       case 'right':
         info.tooltip.style.top = (elCoord.top + elCoord.height / 2) * zoom  +'px';
         info.tooltip.style.left = (elCoord.left + elCoord.width + tooltipArrow) * zoom + 'px';
         break;
       case 'left':
         info.tooltip.style.top = elCoord.top + (elCoord.height / 2) +'px';
         info.tooltip.style.left = elCoord.left - tooltipArrow + 'px';
         break;
       case 'top':
         info.tooltip.style.top = elCoord.top - tooltipArrow +'px';
         info.tooltip.style.left = elCoord.left + (elCoord.width / 2) + 'px';
         break;
       case 'bottom':
         info.tooltip.style.top = elCoord.top + elCoord.height + tooltipArrow +'px';
         info.tooltip.style.left = elCoord.left + (elCoord.width / 2) + 'px';
         break;
     }
   }
  },
  tooltipReposition({dispatch, getters}) {
    if(getters.getIstutorialMode) {
      let element = document.getElementById(getters.getActiveAction.id);
      let tooltip = document.querySelector('.tooltip-tutorial');
      dispatch('sideCalculate', {element, tooltip, side: getters.getActiveAction.position});
    }
  },
  resetTutorial({dispatch, commit}){
    dispatch('removeTooltip');
    dispatch('removeSchematicElement');
    commit('SET_activeActionMainTutorial', 0);
    commit('SET_activePointMainTutorial', 0);
    commit('SET_activeStepMainTutorial', 0);
  },
  resetStoryBoard({commit}) {
    commit('SET_activeStepStoryboard', 0);
    commit('SET_showTutorialStoryBoard', false);
    commit('SET_interactiveInfo', false);
  },
  offTutorial({dispatch, commit, getters, state}) {
    if(getters.getIstutorialMode) {
      commit('SET_isTutorialMode', false);
      commit('SET_showMainTutorialInstruction', false);
      commit('SET_interactiveInfo', false);
      dispatch('resetTutorial');
      dispatch('unlockAllElements');
      dispatch('mod_tracker/EVENT_tutorialModeStop', state.activeStepMainTutorial, {root: true});
    }
  },
  onTutorial({dispatch, commit, getters, rootGetters}, context) {
    commit('SET_isTutorialMode', true);
    commit('SET_showMainTutorialInstruction', true);
    commit('SET_interactiveInfo', false);
    dispatch('lockElements', '#tutorial_layersbar-list');
    dispatch('lockElements', '#tutorial_layer_child-list');
    if(rootGetters['mod_workspace/GET_currentNetworkElementList'] !== null &&
      !getters.getIstutorialMode)  dispatch('mod_workspace/ADD_network')
  },
  removeSchematicElement() {
    let schematicElement = document.querySelector('.schematic');
    if(schematicElement) schematicElement.remove()
  },
  removeDuplicateId() {
    let workspaceElement = document.querySelector('.workspace_content').querySelector('.btn--layersbar');
    if(workspaceElement) {
      workspaceElement.setAttribute('id', '');
    }
  },
  START_storyboard({commit}) {
    commit('SET_showTutorialStoryBoard', true);
    if(router.name !== 'app') router.push({name: 'app'});
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}

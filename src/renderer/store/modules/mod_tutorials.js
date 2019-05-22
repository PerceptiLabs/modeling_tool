import { isNumber } from "util";

const namespaced = true;

const state = {
  isTutorialMode: false,
  showTutorialStoryBoard: false,
  showMainTutorialInstruction: false,
  mainTutorialIsStarted: false,
  interactiveInfo: false,
  
  activeStepStoryboard: 0,
  
  activeStepMainTutorial: 0,
  activePointMainTutorial: 0,
  activeActionMainTutorial: 0,
  
  firstTimeApp: localStorage.showFirstAppTutorial ? false : true,
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
              tooltip: 'Data > Data...',
              position: 'right',
              id: 'tutorial_data',
              status: 'disabled'
            },
            {
              tooltip: 'Data > Data...',
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
              tooltip: 'Select MNIST dataset > Load...',
              position: 'right',
              id: 'tutorial_data-data-1',
              status: 'disabled',
              position_element: {
                top: 6.5,
                left: 18
              },
            },
            {
              tooltip: 'Select MNIST dataset > Load...',
              position: 'right',
              id: 'tutorial_button-load',
              status: 'disabled'
            },
            {
              tooltip: 'Apply loaded MNIST',
              position: 'right',
              id: 'tutorial_button-apply',
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
              content: 'Every input image has been flattened out to a 784x1 array.'
            }
          ]
        },
        {
          status:'disabled',
          content: 'Repeat this step for your label data – also known as ground truth (GT) required to train your supervised AI model.',
          actions: [
            {
              tooltip: 'Data > Data...',
              position: 'right',
              id: 'tutorial_data',
              status: 'disabled'
            },
            {
              tooltip: 'Data > Data...',
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
              tooltip: 'Select MNIST dataset > Load...',
              position: 'right',
              id: 'tutorial_data-data-2',
              status: 'disabled',
            },
            {
              tooltip: 'Select MNIST dataset > Load...',
              position: 'right',
              id: 'tutorial_button-load',
              status: 'disabled'
            },
            {
              tooltip: 'Apply loaded MNIST',
              position: 'right',
              id: 'tutorial_button-apply',
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
              tooltip: 'Processing > Reshape...',
              position: 'right',
              id: 'tutorial_processing',
              status: 'disabled'
            },
            {
              tooltip: 'Processing > Reshape...',
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
              tooltip: 'Select to create a connection...',
              position: 'right',
              id: 'tutorial_list-arrow',
              status: 'disabled'
            },
            {
              tooltip: 'Connect input...',
              position: 'right',
              id: 'tutorial_process-reshape-1',
              schematic: {
                type: 'arrow',
                connection_start: 'tutorial_data-data-1',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Go back to work with items...',
              position: 'right',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Open settings...',
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
          actions: [
            {
              tooltip: 'Reshape to 28x28x1 > Apply changes...',
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
                          <div class="tooltip-tutorial_bold">Patch size:</div> 
                          This is the size of the filter.</br> 
                          E.g. with patch size 3, the </br> 
                          filter will be a square of size 3x3. </br> 
                          <div class="tooltip-tutorial_bold">Hover on input to see more information</div>
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
                          <div class="tooltip-tutorial_bold">Hover on input to see more information</div>
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
                          <div class="tooltip-tutorial_bold">Hover on input to see more information</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_feature-maps',
            }
          ],
          actions: [
            {
              tooltip: 'Deep Learning > Convolution...',
              position: 'right',
              id: 'tutorial_deep-learning', 
              status: 'disabled'
            },
            {
              tooltip: 'Deep Learning > Convolution...',
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
              tooltip: 'Select to create a connection...',
              position: 'right',
              id: 'tutorial_list-arrow',
              status: 'disabled'
            },
            {
              tooltip: 'Connect input...',
              position: 'right',
              id: 'tutorial_convolution-1',
              schematic: {
                type: 'arrow',
                connection_start: 'tutorial_process-reshape-1',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Go back to work with items...',
              position: 'right',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Open settings...',
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
                         <div class="tooltip-tutorial_bold">Hover on input to see more information</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_patch-size',
              status: 'disabled'
            },
/*            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Stride:</div>
                          This is the step size when </br>
                          we slide the filter over the input </br>
                          data to generate feature maps. </br>
                          <div class="tooltip-tutorial_bold">Please press "Tab" button to next input</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_stride',
              status: 'disabled'
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
                          <div class="tooltip-tutorial_bold">Please press "Tab" button to next action</div>
                       </div>`,
              position: 'right',
              id: 'tutorial_feature-maps',
              status: 'disabled'
            },
            {
              tooltip: 'Apply settings',
              position: 'right',
              id: 'tutorial_apply-button',
              status: 'disabled'
            }*/
          ],
          static_info: [
            {
              status:'disabled',
              content: 'Convolution means to slide several filters over the input data.',
            },
            {
              status:'disabled',
              content: 'This generates outputs called feature maps, where each feature'
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
              tooltip: 'Deep Learning > Fully Connected...',
              position: 'right',
              id: 'tutorial_deep-learning', 
              status: 'disabled'
            },
            {
              tooltip: 'Deep Learning > Fully Connected...',
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
              tooltip: 'Select to create a connection...',
              position: 'right',
              id: 'tutorial_list-arrow',
              status: 'disabled'
            },
            {
              tooltip: 'Connect input...',
              position: 'right',
              id: 'tutorial_fully-connected-1',
              schematic: {
                type: 'arrow',
                connection_start: 'tutorial_convolution-1',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Go back to work with items...',
              position: 'right',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Open settings...',
              position: 'right',
              id: 'tutorial_fully-connected-1',
              status: 'disabled'
            }
          ],
          static_info: [
            {
              status:'disabled',
              content: 'This operation matches the size of outputs of your network to the number of classes from your label data',
            }
          ]
        },
        {
          status:'disabled',
          content: 'Set the same number of neurons as there are classes, which in this case is 10 since the images represent digits 0-9. ',
          actions: [
            {
              tooltip: 'Set neurons > Apply changes...',
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
              tooltip: 'Processing > One Hot...',
              position: 'right',
              id: 'tutorial_processing', 
              status: 'disabled'
            },
            {
              tooltip: 'Processing > One Hot...',
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
              tooltip: 'Select to create a connection...',
              position: 'right',
              id: 'tutorial_list-arrow',
              status: 'disabled'
            },
            {
              tooltip: 'Connect input...',
              position: 'right',
              id: 'tutorial_one-hot-1',
              schematic: {
                type: 'arrow',
                connection_start: 'tutorial_data-data-2',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Go back to work with items...',
              position: 'right',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Set classes...',
              position: 'right',
              id: 'tutorial_one-hot-1',
              status: 'disabled'
            },
            {
              tooltip: 'Set 10 > Apply changes...',
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
          actions: [
            {
              tooltip: 'Training > Normal ...',
              position: 'right',
              id: 'tutorial_training', 
              status: 'disabled'
            },
            {
              tooltip: 'Training > Normal ...',
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
              tooltip: 'Select to create a connection...',
              position: 'right',
              id: 'tutorial_list-arrow',
              status: 'disabled'
            },
            {
              tooltip: 'Connect input...',
              position: 'right',
              id: 'tutorial_training-normal-1',
              schematic: {
                type: 'arrow',
                connection_start: 'tutorial_one-hot-1',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Connect input...',
              position: 'right',
              id: 'tutorial_training-normal-1',
              schematic: {
                type: 'arrow',
                connection_start: 'tutorial_fully-connected-1',
              },
              status: 'disabled'
            },
            {
              tooltip: 'Go back to work with items...',
              position: 'right',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Define parameters...',
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
                          <div class="tooltip-tutorial_bold">Hover on input to see more information</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_partition-training-input',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Partition:</div> is the percentage of data </br> that goes into training, validation, </br> and testing respectively. </br>
                          <div class="tooltip-tutorial_bold">Hover on input to see more information</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_partition-validation-input',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Partition:</div> is the percentage of data </br> that goes into training, validation, </br> and testing respectively. </br>
                          <div class="tooltip-tutorial_bold">Hover on input to see more information</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_partition-test-input',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Batch size:</div> to make the training </br> more efficient, you can train on </br> multiples samples at the same time. </br>
                          <div class="tooltip-tutorial_bold">Hover on input to see more information</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_butch-size-input',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Epoch:</div> refers to the number of times </br> you want to run through your entire dataset. </br>
                          <div class="tooltip-tutorial_bold">Hover on input to see more information</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_epochs-input',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Dropout rate:</div> when training we can </br> deactivate half (0.5) of all the </br> learning neurons in each layer in order for </br> the network to learn in a  more general way. 
                          </br></br> Note: this has to be activated independently </br> for each deep learning layer.</br>
                          <div class="tooltip-tutorial_bold">Hover on input to see more information</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_drop-rate-input',
            },
          ],
          actions: [
            {
              tooltip: 'Run training...',
              position: 'bottom',
              id: 'tutorial_run-training-button', 
              status: 'disabled'
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Partition:</div> is the percentage of data </br> that goes into training, validation, </br> and testing respectively. </br>
                          <div class="tooltip-tutorial_bold">Hover on input to see more information</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_partition-training-input',
              status: 'disabled'
            },
            /*{
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Partition:</div> is the percentage of data </br> that goes into training, validation, </br> and testing respectively. </br>
                          <div class="tooltip-tutorial_bold">Please press "Tab" button to next input</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_partition-validation-input',
              status: 'disabled'
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Partition:</div> is the percentage of data </br> that goes into training, validation, </br> and testing respectively. </br>
                          <div class="tooltip-tutorial_bold">Please press "Tab" button to next input</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_partition-test-input',
              status: 'disabled'
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Batch size:</div> to make the training </br> more efficient, you can train on </br> multiples samples at the same time. </br>
                          <div class="tooltip-tutorial_bold">Please press "Tab" button to next input</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_butch-size-input',
              status: 'disabled'
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Epoch:</div> refers to the number of times </br> you want to run through your entire dataset. </br>
                          <div class="tooltip-tutorial_bold">Please press "Tab" button to next input</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_epochs-input',
              status: 'disabled'
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Dropout rate:</div> when training we can </br> deactivate half (0.5) of all the </br> learning neurons in each layer in order for </br> the network to learn in a  more general way. 
                          </br></br> Note: this has to be activated independently </br> for each deep learning layer.</br>
                          <div class="tooltip-tutorial_bold">Please press "Tab" button to next action</div>
                        </div>`,
              position: 'right',
              id: 'tutorial_drop-rate-input',
              status: 'disabled'
            },
            {
              tooltip: 'Click Apply',
              position: 'right',
              id: 'tutorial_apply-button',
              status: 'disabled'
            }*/
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
          content: 'The top window shows training <div class="marker">Statistics</div> for the overall network. Press <div class="marker">"Next"</div> to continue',
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
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'The <div class="marker">Pause</div> to learn  further details',
          actions: [
            {
              tooltip: 'Pause...',
              position: 'bottom',
              id: 'tutorial_pause-training',
              status: 'disabled',
            }
          ]
        },
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'Click <div class="marker">Reshape</div> in the <div class="marker">Map View</div> </br> Notice the corresponding display in the <div class="marker">ViewBox</div>',
          actions: [
            { 
              tooltip: 'Click Reshape...',
              position: 'right',
              id: 'tutorial_process-reshape-1',
              status: 'disabled',
            }
          ]
        },
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'Click <div class="marker">Fully Connected (FC)</div> in the <div class="marker">Map View</div> See that the output line in FC is the same as<div class="marker">ViewBox</div> Press <div class="marker">"Next"</div> to continue',
          actions: [
            { 
              tooltip: 'This is the image that <br/> the AI trying to classify. </br> Press"Next" to continue',
              position: 'right',
              id: 'tutorial_view-box',
              status: 'disabled',
              next: true
            },
            { 
              tooltip: 'Click Fully Connected...',
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
                          <div class="tooltip-tutorial_bold">Prediction:</div> Overview of the </br> network perfomance
                        </div>`,
              position: 'right',
              id: 'tutorial_prediction-tab',
              status: 'disabled',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Accuracy:</div> Overall </br> performance of a network. </br> The higher the accuracy, </br> the better it is at learning. 
                        </div>`,
              position: 'right',
              id: 'tutorial_accuracy-tab',
              status: 'disabled',
            },
            {
              tooltip: `<div class="tooltip-tutorial_italic">
                          <div class="tooltip-tutorial_bold">Loss:</div> How much error there is in your predictions.
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
              tooltip: 'Unpause...',
              position: 'bottom',
              id: 'tutorial_pause-training',
              status: 'disabled',
            }
          ]
        },
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'Weight when training is complete for this network.',
          actions: [
            {
              tooltip: 'Training is complete for this network...',
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
              tooltip: 'Click to start test...',
              position: 'right',
              status: 'disabled',
              id:'tutorial_run-test-button'
            }
          ]
        },
      ]
    },
    testing: {
      title: 'Step 9. Testing',
      points: [
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'Testing shows how general your model is, i.e. to what extent can it classify things it has never seen before',
          actions: [
            {
              tooltip: 'Explore view controls...',
              position: 'right',
              status: 'disabled',
              id:'tutorial_play-test-button'
            }
          ]
        }
      ]
    },
    save_and_export: {
      title: 'Step 10. Save and export',
      points: [
        {
          status:'last step',
          actions: [
            {
              status: 'disabled',
            }
          ]
        }
      ]
    }
  }
};

const getters = {
  getIterective(state) {
    return state.interective
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
   let action = getters.getActivePoint ? getters.getActivePoint.actions[state.activeActionMainTutorial] : ''
   return action
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
    state.activeStepStoryboard = value;
  },
  SET_showTutorialStoryBoard(state, value) {
    state.showTutorialStoryBoard = value;
    state.firstTimeApp = value;
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
    } else if(value === 'next') {
      state.activeActionMainTutorial++
    }
  },
  SET_firstTimeApp(state, value) {
    localStorage.showFirstAppTutorial = value;
    state.showTutorial = value;
    state.firstTimeApp = value;
  },
  SET_pointActivate(state, value,) {
    let points = state.interective[value.step].points;
    points[value.point].status = value.status;

  },
  SET_activeAction(state, value) {
    let actions = state.interective[value.step].points[value.point].actions;
    actions[value.action].status = value.status
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
          dispatch('checkActiveActionAndPoint', value)
        }
        else {
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
      dispatch('createTooltip', {id: getters.getActiveAction.id, tooltip: getters.getActiveAction.tooltip});
      dispatch('removeSchematicElement');
      dispatch('drawSchematicElement', getters.getActiveAction.schematic);
      dispatch('showHoverInfo');
    } 
    else { // all actions are done
      dispatch('removeTooltip');
      dispatch('nextPoint');
      if(getters.getActivePoint) {
        commit('SET_pointActivate', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, status: 'active'});
        dispatch('createTooltip', {id: getters.getActiveAction.id, tooltip: getters.getActiveAction.tooltip});
      }
      else { //all points are done
        dispatch('removeTooltip');
        commit('SET_activePointMainTutorial', 0)
      }
    }
  },
  createTooltip({getters, dispatch}, info) {
    dispatch('removeTooltip');
    let element = document.getElementById(info.id);
    if(getters.getActiveAction.tooltip) { 
      let tooltipBlock = document.createElement('div');
      tooltipBlock.classList.add('tooltip-tutorial', `tooltip-tutorial--${getters.getActiveAction.position}`);
      tooltipBlock.innerHTML = info.tooltip;
      element.appendChild(tooltipBlock);
    }
  },
  removeTooltip() {
    let activeTooltip = document.querySelector('.tooltip-tutorial');
    if(activeTooltip) activeTooltip.remove()
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
      }
    }
  },
  showHoverInfo({getters, dispatch}) {
    const elements = document.querySelectorAll('.form_input[data-tutorial-hover-info]');
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
  },
  resetTutorial({dispatch, commit}){
    dispatch('removeTooltip');
    dispatch('removeSchematicElement');
    commit('SET_activeActionMainTutorial', 0);
    commit('SET_activePointMainTutorial', 0);
    commit('SET_activeStepMainTutorial', 0);
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
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}

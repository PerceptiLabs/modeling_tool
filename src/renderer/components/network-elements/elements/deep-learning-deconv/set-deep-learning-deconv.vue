<template lang="pug">
  net-base-settings(
    :layer-code="currentEl.layerCode.length"
    :first-tab="currentEl.layerSettingsTabName"
    @press-apply="saveSettings($event)"
    @press-update="updateCode"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.dimension")
          .form_label Dimension:
          .form_input
            base-radio(group-name="group" value-input="Automatic" v-model="settings.Deconv_dim")
              span Automatic
            base-radio(group-name="group" value-input="1D" v-model="settings.Deconv_dim")
              span 1D
            base-radio(group-name="group" value-input="2D" v-model="settings.Deconv_dim")
              span 2D
            base-radio(group-name="group" value-input="3D" v-model="settings.Deconv_dim")
              span 3D
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.stride")
          .form_label Stride:
          .form_input
            input(type="text" v-model="settings.Stride")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.featureMaps")
          .form_label Feature maps:
          .form_input
            input(type="text" v-model="settings.Feature_maps")

      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.zeroPadding")
          .form_label Zero-padding:
          .form_input
            base-radio(group-name="group3" value-input="'SAME'"  v-model="settings.Padding")
              span SAME
            base-radio(group-name="group3" value-input="'VALID'"  v-model="settings.Padding")
              span VALID
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.activationFunction")
          .form_label Activation function:
          .form_input
            base-radio(group-name="group1" value-input="None"  v-model="settings.Activation_function")
              span None
            base-radio(group-name="group1" value-input="Sigmoid"  v-model="settings.Activation_function")
              span Sigmoid
            base-radio(group-name="group1" value-input="ReLU"  v-model="settings.Activation_function")
              span ReLU
            base-radio(group-name="group1" value-input="Tanh"  v-model="settings.Activation_function")
              span Tanh
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.dropout")
          .form_label Dropout:
          .form_input
            base-radio(group-name="group5" :value-input="false"  v-model="settings.Dropout")
              span None
            base-radio(group-name="group5" :value-input="true"  v-model="settings.Dropout")
              span Sigmoid
    template(slot="Code-content")
      settings-code(v-model="coreCode")

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetDeepLearningDeconv',
  mixins: [mixinSet],
  data() {
    return {
      settings: {
        Deconv_dim: "2D", //Automatic, 1D, 2D, 3D
        Stride: "2",
        Padding: "'SAME'", //'SAME', 'VALID'
        Feature_maps: "8",
        Activation_function: "Sigmoid", //Sigmoid, ReLU, Tanh, None
        Dropout: false, //True, False
      },
      interactiveInfo: {
        dimension: {
          title: 'Dimension',
          text: 'Choose which type of convolutional </br> operation to use'
        },
        stride: {
          title: 'Stride',
          text: 'Set the stride'
        },
        featureMaps: {
          title: 'Feature maps',
          text: 'Set the number of feature maps.'
        },
        zeroPadding: {
          title: 'Zero-padding',
          text: 'Choose to use zero-padding or not.'
        },
        activationFunction: {
          title: 'Activation function',
          text: 'Choose which activation function to use'
        },
        dropout: {
          title: 'Dropout',
          text: 'Choose if dropout should </br> be used or not'
        }
      },
    }
  },
  computed: {
    settingsCode() {
      let dim = '';
      let activeFunc = '';
      let pooling = '';

      switch (this.settings.Deconv_dim) {
        case 'Automatic':
          dim = `${this.settings.Deconv_dim} = str(len(X.get_shape())-1) + "D";`;
          break;
        case '1D':
          dim = `shape=[${this.settings.Stride},${this.codeInputDim}[-1], ${this.settings.Feature_maps}];
initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(${this.settings.Stride}**2 *${this.settings.Feature_maps})));
W = tf.Variable(initial);
initial = tf.constant(0.1, shape=[${this.settings.Feature_maps}]);
b=tf.Variable(initial);
output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*${this.settings.Stride} for node_shape in ${this.codeInputDim}]+[${this.settings.Feature_maps}]);
node = tf.nn.conv1d_transpose(X, W, output_shape, ${this.settings.Stride},padding=${this.settings.Padding})${this.settings.Dropout ? '\nnode=tf.nn.dropout(node, keep_prob);' : ';'}
node=node+b;`;
          break;
        case '2D':
          dim = `shape=[${this.settings.Stride},${this.settings.Stride},${this.codeInputDim}[-1],${this.settings.Feature_maps}];
initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(${this.settings.Stride}**2 * ${this.settings.Feature_maps})));
W = tf.Variable(initial);
initial = tf.constant(0.1, shape=[${this.settings.Feature_maps}]);
b=tf.Variable(initial);
output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*${this.settings.Stride} for node_shape in ${this.codeInputDim}]+[${this.settings.Feature_maps}]);
node = tf.nn.conv2d_transpose(X, W, output_shape, strides=[1, ${this.settings.Stride}, ${this.settings.Stride}, 1], padding=${this.settings.Padding})${this.settings.Dropout ? '\nnode=tf.nn.dropout(node, keep_prob);' : ';'}
node=node+b;`;
          break;
        case '3D':
          dim = `shape=[${this.settings.Stride},${this.settings.Stride},Stride"],${this.codeInputDim}[-1],${this.settings.Feature_maps}];
initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(${this.settings.Stride}**2 * ${this.settings.Feature_maps})));
W = tf.Variable(initial);
initial = tf.constant(0.1, shape=[${this.settings.Feature_maps}]);
b=tf.Variable(initial);
output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*${this.settings.Stride} for node_shape in ${this.codeInputDim}]+[${this.settings.Feature_maps}]);
node = tf.nn.conv3d_transpose(X, W, output_shape, strides=[1, ${this.settings.Stride}, ${this.settings.Stride}, ${this.settings.Stride}, 1], padding=${this.settings.Padding})${this.settings.Dropout ? '\nnode=tf.nn.dropout(node, keep_prob);' : ';'}
node=node+b;`;
          break;
      }
      switch (this.settings.Activation_function) {
        case 'Sigmoid':
          activeFunc = `Y=tf.sigmoid(node);`;
          break;
        case 'ReLU':
          activeFunc = `Y=tf.nn.relu(node);`;
          break;
        case 'Tanh':
          activeFunc = `Y=tf.tanh(node);`;
          break;
        case 'None':
          activeFunc = `Y=node;`;
          break;
      }

      if(this.settings.PoolBool) {
        if (this.settings.Pooling === "Max") {
          pooling = `Y=max_pool(Y, ${this.settings.Pool_area}, ${this.settings.Stride},${this.settings.Padding},${this.settings.Conv_dim});`;
        } else {
          pooling = `Y=tf.nn.pool(Y, window_shape=${this.settings.Pool_area},pooling_type='AVG',${this.settings.Padding},strides=${this.settings.Stride});`
        }
      }
      return `${dim}\n${activeFunc}\n${pooling}`
    }
  }
}
</script>

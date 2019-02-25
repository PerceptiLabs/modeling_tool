<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
      :disabled="tabSelected != i"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body(
        :class="{'active': tabSelected == 0}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              .form_label Dimension:
              .form_input
                base-radio(groupName="group" valueInput="Automatic" v-model="settings.Deconv_dim")
                  span Automatic
                base-radio(groupName="group" valueInput="1D" v-model="settings.Deconv_dim")
                  span 1D
                base-radio(groupName="group" valueInput="2D" v-model="settings.Deconv_dim")
                  span 2D
                base-radio(groupName="group" valueInput="3D" v-model="settings.Deconv_dim")
                  span 3D
          .settings-layer_section
            .form_row
              .form_label Stride:
              .form_input
                input(type="text" v-model="settings.Stride")
          .settings-layer_section
            .form_row
              .form_label Feature maps:
              .form_input
                input(type="text" v-model="settings.Feature_maps")

          .settings-layer_section
            .form_row
              .form_label Zero-padding:
              .form_input
                base-radio(groupName="group3" valueInput="'SAME'"  v-model="settings.Padding")
                  span SAME
                base-radio(groupName="group3" valueInput="'VALID'"  v-model="settings.Padding")
                  span VALID
          .settings-layer_section
            .form_row
              .form_label Activation function:
              .form_input
                base-radio(groupName="group1" valueInput="None"  v-model="settings.Activation_function")
                  span None
                base-radio(groupName="group1" valueInput="Sigmoid"  v-model="settings.Activation_function")
                  span Sigmoid
                base-radio(groupName="group1" valueInput="ReLU"  v-model="settings.Activation_function")
                  span ReLU
                base-radio(groupName="group1" valueInput="Tanh"  v-model="settings.Activation_function")
                  span Tanh
          .settings-layer_section
            .form_row
              .form_label Dropout:
              .form_input
                base-radio(groupName="group5" :valueInput="false"  v-model="settings.Dropout")
                  span None
                base-radio(groupName="group5" :valueInput="true"  v-model="settings.Dropout")
                  span Sigmoid
          .settings-layer_foot
            button.btn.btn--primary(type="button" @click="applySettings") Apply

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
          :the-code="coreCode"
        )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

export default {
  name: 'SetDeepLearningDeconv',
  mixins: [mixinSet],
  components: {
    SettingsCode
  },
  data() {
    return {
      tabs: ['Settings', 'Code'],
      settings: {
        Deconv_dim: "2D", //Automatic, 1D, 2D, 3D
        Stride: "2",
        Padding: "'SAME'", //'SAME', 'VALID'
        Feature_maps: "8",
        Activation_function: "Sigmoid", //Sigmoid, ReLU, Tanh, None
        Dropout: false, //True, False
      }
    }
  },
  computed: {
    coreCode() {
      let addPooling = '';
      //       Activation function
      // • If Sigmoid:
      //         Y=tf.sigmoid(node)
      // • If ReLU:
      //         Y=tf.nn.relu(node)
      // • If Tanh:
      //         Y=tf.tanh(node)
      // • If None:
      //         Y=node
      switch (this.settings.Conv_dim) {
        case 'Automatic':
          return `properties["${this.settings.Conv_dim}"] = str(len(X.get_shape())-1) + "D"
                  ${addPooling}`
          break;
        case '1D':
          return `shape=[properties["${this.settings.Stride}"],X.get_shape()[-1].value, properties["${this.settings.Feature_maps}"]];
                  initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(properties["${this.settings.Stride}"]**2 *properties["${this.settings.Feature_maps}"])));
                  W = tf.Variable(initial);
                  initial = tf.constant(0.1, shape=[properties["${this.settings.Feature_maps}"]]);
                  b=tf.Variable(initial);
                  output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*properties["${this.settings.Stride}"] for node_shape in X.get_shape().as_list()[1:-1]]+[properties["${this.settings.Feature_maps}"]]);
                  node = tf.nn.conv1d_transpose(X, W, output_shape, properties["${this.settings.Stride}"],padding=properties["${this.settings.Padding}"]);
                  node=tf.nn.dropout(node, keep_prob);
                  node=node+b
                  ${addPooling}`
          break;
        case '2D':
          return `shape=[properties["${this.settings.Stride}"],properties["${this.settings.Stride}"],X.get_shape()[-1].value,properties["${this.settings.Feature_maps}"]];
                  initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(properties["${this.settings.Stride}"]**2 * properties["${this.settings.Feature_maps}"])));
                  W = tf.Variable(initial);
                  initial = tf.constant(0.1, shape=[properties["${this.settings.Feature_maps}"]]);
                  b=tf.Variable(initial);
                  output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*"+properties["${this.settings.Stride}"]+" for node_shape in X.get_shape().as_list()[1:-1]]+["+properties["${this.settings.Feature_maps}"]+"]);
                  node = tf.nn.conv2d_transpose(X, W, output_shape, strides=[1, properties["${this.settings.Stride}"], properties["${this.settings.Stride}"], 1], padding=properties["${this.settings.Padding}"]);
                  node=tf.nn.dropout(node, keep_prob);
                  node=node+b
                  ${addPooling}`
          break;
        case '3D':
          return `shape=[properties["${this.settings.Stride}"],properties["${this.settings.Stride}"],properties["Stride"],X.get_shape()[-1].value,properties["${this.settings.Feature_maps}"]];
                  initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(properties["${this.settings.Stride}"]**2 * properties["${this.settings.Feature_maps}"])));
                  W = tf.Variable(initial);
                  initial = tf.constant(0.1, shape=[properties["${this.settings.Feature_maps}"]]);
                  b=tf.Variable(initial);
                  output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*properties["${this.settings.Stride}"] for node_shape in X.get_shape().as_list()[1:-1]]+[properties["${this.settings.Feature_maps}"]]);
                  node = tf.nn.conv3d_transpose(X, W, output_shape, strides=[1, properties["${this.settings.Stride}"], properties["${this.settings.Stride}"], properties["${this.settings.Stride}"], 1], padding=properties["${this.settings.Padding}"]);
                  node=tf.nn.dropout(node, keep_prob);
                  node=node+b
                  ${addPooling}`
          break;
      }
    }
  }
}
</script>

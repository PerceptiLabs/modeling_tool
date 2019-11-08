import {mapActions} from "vuex";

const workspaceScale = {
  updated() {
    console.log('updated');
  },
  computed: {

  },
  watch: {

  },
  methods: {
    ...mapActions({
      SET_elementNetworkWindow: 'mod_workspaceHelpers/SET_elementNetworkWindow',
      SET_elementNetworkField: 'mod_workspaceHelpers/SET_elementNetworkField',
    }),
  }
};

export default workspaceScale

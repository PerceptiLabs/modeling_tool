import { App as VueApp } from "vue";
import VueSelect from "vue-next-select";
import "vue-next-select/dist/index.min.css";
import "./custom.scss";

const setup = (appInstance: VueApp<Element>) => {
  appInstance.component("v-select", VueSelect);
};

export default setup;

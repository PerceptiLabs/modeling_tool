import { App as VueApp } from "vue";

import setupVueSelect from "./vue-next-select";
import setupFontAwesome from "./font-awesome";

export default function setup(appInstance: VueApp<Element>) {
  setupVueSelect(appInstance);
  setupFontAwesome(appInstance);
}

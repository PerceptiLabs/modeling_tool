import { App as VueApp } from "vue";

import setupTooltip from "./Tooltip";

export default function setup(appInstance: VueApp<Element>) {
  setupTooltip(appInstance);
}

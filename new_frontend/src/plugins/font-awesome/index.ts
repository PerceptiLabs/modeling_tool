import { App as VueApp } from "vue";
import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

import {
  faSearch,
  faPlus,
  faExternalLinkAlt,
  faTrashAlt,
} from "@fortawesome/free-solid-svg-icons";

library.add(faSearch, faPlus, faExternalLinkAlt, faTrashAlt);

const setup = (appInstance: VueApp<Element>) => {
  appInstance.component("fa-icon", FontAwesomeIcon);
};

export default setup;

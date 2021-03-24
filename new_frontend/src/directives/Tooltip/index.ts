/**
 * Tooltip Directive
 *
 * Args: direction (top/right/left/bottom/cursor default: cursor)
 * Modifiers: predefined template bindings
 *
 */
import { App as VueApp, Directive, DirectiveBinding } from "vue";
import {
  TOOLTIP_BINDING_KEY,
  TooltipPosition,
  calculatePosition,
  generateTooltipHTML,
} from "./utils";
import "./styles.scss";

function insertTooltip(event: MouseEvent) {
  const binding: DirectiveBinding<string> = event.target[TOOLTIP_BINDING_KEY];

  // Arg is for direction
  const position = (binding.arg || "cursor") as TooltipPosition;

  // Modifiers are for predefined templates
  const element = document.createElement("div");
  element.classList.add("tooltip", `tooltip--${position}`);
  element.innerHTML = generateTooltipHTML(null, binding.value);
  (event.target as HTMLElement).appendChild(element);

  calculatePosition(event.target as HTMLElement, element, position, 1);
}

function removeTooltip(event: MouseEvent) {
  const tooltip = (event.currentTarget as HTMLElement).querySelector<
    HTMLElement
  >(".tooltip");

  if (tooltip) {
    tooltip.remove();
  }
}

function moveTooltip(event: MouseEvent) {
  const wrapper = event.currentTarget as HTMLElement;
  const rect = wrapper.getBoundingClientRect();
  const tooltip = wrapper.querySelector<HTMLElement>(".tooltip");

  tooltip.style.left = event.clientX - rect.left + 10 + "px";
  tooltip.style.top = event.clientY - rect.top + 5 + "px";
}

export default function tooltipDirective(app: VueApp<Element>) {
  app.directive("tooltip", {
    mounted(el, binding) {
      el[TOOLTIP_BINDING_KEY] = binding;
      el.classList.add("tooltip-wrap");

      el.addEventListener("mouseenter", insertTooltip);
      el.addEventListener("mouseleave", removeTooltip);

      console.log("mounted", binding);

      if ((binding.arg || "cursor") === "cursor") {
        el.addEventListener("mousemove", moveTooltip);
      }
    },

    updated(el, binding) {
      el.removeEventListener("mouseenter", insertTooltip);
      el.removeEventListener("mouseleave", removeTooltip);
      el.removeEventListener("mousemove", moveTooltip);

      el.addEventListener("mouseenter", insertTooltip);
      el.addEventListener("mouseleave", removeTooltip);

      console.log("updated", binding);

      if ((binding.arg || "cursor") === "cursor") {
        el.addEventListener("mousemove", moveTooltip);
      }
    },

    unmounted(el) {
      el.removeEventListener("mouseenter", insertTooltip);
      el.removeEventListener("mouseleave", removeTooltip);
      el.removeEventListener("mousemove", moveTooltip);
    },
  } as Directive<Element, string>);
}

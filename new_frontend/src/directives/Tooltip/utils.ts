export const TOOLTIP_BINDING_KEY = "tooltipBinding";
export type TooltipPosition =
  | "right"
  | "right-wrap-text"
  | "left"
  | "top"
  | "bottom"
  | "bottom-right"
  | "cursor";
export type TooltipTemplate = "project" | null;

export function generateTooltipHTML(_template: TooltipTemplate, value: string) {
  return value;
}

export function calculatePosition(
  element: HTMLElement,
  tooltip: HTMLElement,
  side: TooltipPosition,
  zoom = 1,
) {
  const elCoord = element.getBoundingClientRect();
  const clCoord = tooltip.getBoundingClientRect();
  const tooltipArrow = 10;

  switch (side) {
    case "right":
      tooltip.style.top = (elCoord.height / 2) * zoom + "px";
      tooltip.style.left = elCoord.width * zoom + "px";
      break;
    case "right-wrap-text":
      tooltip.style.top = (elCoord.height / 2) * zoom + "px";
      tooltip.style.left = (elCoord.width + tooltipArrow) * zoom + "px";
      break;
    case "left":
      tooltip.style.top = (elCoord.height / 2) * zoom + "px";
      tooltip.style.left = -clCoord.width * zoom + "px";
      break;
    case "top":
      tooltip.style.top = -clCoord.height * zoom + "px";
      tooltip.style.left = (elCoord.width / 2) * zoom + "px";
      break;
    case "bottom":
      tooltip.style.top = elCoord.height * zoom + "px";
      tooltip.style.left = (elCoord.width / 2) * zoom + "px";
      break;
    case "bottom-right":
      tooltip.style.top = (elCoord.height + tooltipArrow) * zoom + "px";
      tooltip.style.left = tooltipArrow * zoom + "px";
      break;
  }
}

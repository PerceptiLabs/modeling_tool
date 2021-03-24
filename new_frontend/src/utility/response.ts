import chanageCaseObject from "change-case-object";

export const parseResponse = <T extends {}>(response: T | Array<T>) => {
  return chanageCaseObject.camelCase(response);
};

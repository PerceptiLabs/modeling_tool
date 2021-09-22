import { getFirstElementFromObject } from "@/core/helpers";

export const getDatasetPath = (datasetSettings) => {
  if (datasetSettings.csv_path) {
    return datasetSettings.csv_path;
  } else if (datasetSettings.featureSpecs && Object.keys(datasetSettings).length > 0) {
    return getFirstElementFromObject(datasetSettings.featureSpecs).csv_path;
  } else {
    return null;
  }
}

export const formatCSVTypesIntoKernelFormat = (csvData) => {
  const payload = {};
  for (const [idx, val] of csvData.columnNames.entries()) {
    const sanitizedVal = val.replace(/^\n|\n$/g, "");
    payload[sanitizedVal] = {
      iotype: csvData.ioTypes[idx],
      datatype: csvData.dataTypes[idx],
      preprocessing: csvData.preprocessingTypes[idx],
    }
  }
  return payload;
}

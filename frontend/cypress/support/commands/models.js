import { getModelContent } from "../../plugins/model-creation";

Cypress.Commands.add("deleteModel", (modelId) => {
  return cy.ryggRequest(`/models/${modelId}/`).then((modelResponse) => {
    const model = modelResponse.body;

    // delete model directory
    cy.ryggRequest(`/directories`, "DELETE", {
      path: model.location,
    });

    // delete model from rygg
    cy.ryggRequest(`/models/${modelId}/`, "DELETE");
  });
});

Cypress.Commands.add("deleteAllModels", () => {
  return cy.ryggRequest("/projects").then((projectResponse) => {
    const projects = projectResponse.body.results;

    projects.forEach((project) => {
      project.models.forEach((modelId) => {
        cy.deleteModel(modelId);
      });
    });
  });
});

Cypress.Commands.add("createMnistModel", (modelName) => {
  cy.ryggRequest("/projects").then((projectResponse) => {
    const project = projectResponse.body.results[0];

    cy.fixture("modelConfig").then(({ dataCSVPath }) => {
      cy.ryggRequest("/models/", "POST", {
        name: modelName,
        project: project.project_id,
        location: project.default_directory + "/" + modelName,
      }).then((modelResponse) => {
        const model = modelResponse.body;

        const modelInfo = getModelContent(model, dataCSVPath);

        cy.ryggRequest(
          "/json_models",
          "POST",
          {
            path: model.location,
          },
          modelInfo
        );
      });
    });
  });
});

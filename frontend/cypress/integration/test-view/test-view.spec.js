describe("Test view", () => {
  before(() => {
    cy.fixture("userCredentials").then((user) => {
      cy.kcLogin(user.email, user.password);
    });
    cy.deleteAllModels();
    cy.createMnistModel("Trained Classification Model 1");
    cy.createMnistModel("Trained Classification Model 2");
    cy.createMnistModel("Not Trained Model 1");
    cy.createMnistModel("Not Trained Model 2");
    cy.createMnistModel("Not Trained Model 3");

    cy.trainModel("Trained Classification Model 1");
    cy.trainModel("Trained Classification Model 2");

    cy.visit("/test");
  });

  it("Should display models with tests", () => {
    // click run test button
    cy.get(".test-view")
      .get(".run-test-button")
      .click();

    // open dropdown
    cy.get(".test-configuration-popup")
      .get(".custom-select")
      .click();

    // check dropdown list
    const dropdownOptions = [
      "Select All",
      "Trained Classification Model 1",
      "Trained Classification Model 2",
    ];
    cy.get(".test-configuration-popup")
      .get(".custom-select_option")
      .its("length")
      .should("eq", dropdownOptions.length);
    cy.get(".test-configuration-popup")
      .get(".custom-select_option")
      .each((option, index) => {
        cy.wrap(option).should("contain.text", dropdownOptions[index]);
      });
  });

  it("select classification model should enable proper options", () => {
    // Select 2 classification models
    cy.get(".test-configuration-popup")
      .get(".custom-select_option")
      .contains("Trained Classification Model 1")
      .click();
    cy.get(".test-configuration-popup")
      .get(".custom-select_option")
      .contains("Trained Classification Model 2")
      .click();

    // close popup
    cy.get(".test-configuration-popup")
      .get(".custom-select")
      .click();

    //
    cy.get(".test-configuration-popup")
      .get("#confusion_matrix.custom-checkbox")
      .should("not.have.class", "disabled");
    cy.get(".test-configuration-popup")
      .get("#classification_metrics.custom-checkbox")
      .should("not.have.class", "disabled");
    cy.get(".test-configuration-popup")
      .get("#segmentation_metrics.custom-checkbox")
      .should("have.class", "disabled");
  });

  it("should run tests correctly", () => {
    // select options
    cy.get(".test-configuration-popup")
      .get("#confusion_matrix.custom-checkbox")
      .click();
    cy.get(".test-configuration-popup")
      .get("#classification_metrics.custom-checkbox")
      .click();

    cy.get(".test-configuration-popup")
      .get(".popup_foot")
      .contains("Run Test")
      .click();

    cy.get(".test-overlay .chart-spinner").should("exist");
  });

  it("should stop tests", () => {
    cy.get(".test-overlay .stop-test").click();

    cy.get(".test-overlay .chart-spinner").should("not.exist");
    cy.get(".test-view")
      .get(".run-test-button")
      .should("exist");
  });

  it("should tests succeed", () => {
    // click run test button
    cy.get(".test-view")
      .get(".run-test-button")
      .click();

    cy.get(".test-configuration-popup")
    .get(".custom-select")
    .click();

    // Select 2 classification models
    cy.get(".test-configuration-popup")
      .get(".custom-select_option")
      .contains("Trained Classification Model 1")
      .click();
    cy.get(".test-configuration-popup")
      .get(".custom-select_option")
      .contains("Trained Classification Model 2")
      .click();

    // close popup
    cy.get(".test-configuration-popup")
      .get(".custom-select")
      .click();

    // select options
    cy.get(".test-configuration-popup")
      .get("#confusion_matrix.custom-checkbox")
      .click();
    cy.get(".test-configuration-popup")
      .get("#classification_metrics.custom-checkbox")
      .click();

    cy.get(".test-configuration-popup")
      .get(".popup_foot")
      .contains("Run Test")
      .click();

    cy.get(".test-overlay .chart-spinner").should("exist");

    cy.get(".test-overlay .chart-spinner", {
      timeout: 10 * 60 * 1000,
    }).should("not.exist");

    cy.get('.test-view .chart-container').should('exist');
  });
});

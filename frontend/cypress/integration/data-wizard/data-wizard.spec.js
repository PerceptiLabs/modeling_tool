describe("data-wizard", () => {
  before(() => {
    cy.fixture("userCredentials").then((user) => {
      cy.kcLogin(user.email, user.password);
    });
  });

  beforeEach(() => {
    cy.deleteAllModels();

    cy.visit("/");
  });

  function preSetup() {
    // Click Create button in the toolbar
    cy.get(
      'span[data-tutorial-target="tutorial-model-hub-new-button"]'
    ).click();

    // Click Load CSV button
    cy.get(".select-model-modal")
      .find('button[data-tutorial-target="tutorial-data-wizard-load-csv"]')
      .click();

    // Select mnist_small folder
    cy.get(".select-model-modal .popup-global .filepicker")
      .contains("mnist_small")
      .dblclick();
    cy.get(".select-model-modal .popup-global .filepicker")
      .contains("data.csv")
      .dblclick();

    // TODO: wait for file load

    // Select IO types
    cy.get(".select-model-modal .dataset-settings .footer-actions")
      .find("button.next-to-settings-btn")
      .should("be.disabled");

    cy.get(
      '.select-model-modal .dataset-settings tr[test-id="io-selection-row"]'
    )
      .find("td > .custom-select.active")
      .find("button.custom-select_view")
      .click();

    cy.get(
      '.select-model-modal .dataset-settings tr[test-id="io-selection-row"] td'
    )
      .find(".custom-select_option-list.open")
      .find(".custom-select_option")
      .contains("Input")
      .click();

    cy.get(
      '.select-model-modal .dataset-settings tr[test-id="io-selection-row"]'
    )
      .find("td > .custom-select.active")
      .find("button.custom-select_view")
      .click();

    cy.get(
      '.select-model-modal .dataset-settings tr[test-id="io-selection-row"] td'
    )
      .find(".custom-select_option-list.open")
      .find(".custom-select_option")
      .contains("Target")
      .click();

    cy.get(".select-model-modal .dataset-settings .footer-actions")
      .find("button.next-to-settings-btn")
      .click();
  }

  it("Should be able to create a model", () => {
    preSetup();

    // Training settings page
    cy.get(".select-model-modal .model-run-settings-page .footer-actions")
      .find("button.action-button")
      .contains("Customize")
      .click();

    // TODO: wait for model build

    cy.location("pathname").should("equal", "/app");
  });
});

describe("Workspace", () => {
  before(() => {
    cy.fixture("userCredentials").then((user) => {
      cy.kcLogin(user.email, user.password);
    });
    cy.deleteAllModels();
    cy.createMnistModel("Model 1");

    cy.visit("/");

    // Click Model 1
    cy.get(".models-list .models-list-row.model-list-item")
      .first()
      .find(".column-1 .model-name-wrapper")
      .click();
  });

  const createRandomElement = (posX, posY) => {
    // Select random header
    cy.get(".layer-list-header")
      .its("length")
      .then((headersCount) => {
        let selected = Cypress._.random(headersCount - 1);
        cy.get(".layer-list-header")
          .eq(selected)
          .click();
      });
    //   Select random item
    cy.get(".active + ul.layer_child-list > .layer_child-list-item")
      .its("length")
      .then((itemsCount) => {
        let selected = Cypress._.random(itemsCount - 1);
        cy.get(".active + ul.layer_child-list > .layer_child-list-item")
          .eq(selected)
          .click();
      });
    cy.get(".network-field").trigger("mousemove", {
      clientX: 670,
      clientY: 441,
      screenX: 670,
      screenY: 545,
      pageX: 670,
      pageY: 441,
    });
    cy.get(".network-field").click(posX, posY);
  };

  const createElement = (header, item, pos) => {
    // Select random header
    cy.get(".layer-list-header")
      .contains(header)
      .click();
    //   Select random item
    cy.get(".active + ul.layer_child-list > .layer_child-list-item")
      .contains(item)
      .click();
    cy.get(".network-field").trigger("mousemove", {
      clientX: 670,
      clientY: 441,
      screenX: 670,
      screenY: 545,
      pageX: 670,
      pageY: 441,
    });
    cy.get(".network-field").click(pos.X, pos.Y);
  };

  it("should land on workspace", () => {
    cy.location("pathname").should("equal", "/app");
  });

  it("Can add a component", () => {
    cy.get(".net-element")
      .its("length")
      .as("componentsCount");
    createRandomElement(50, 300);

    cy.get("@componentsCount").then((componentCounts) => {
      cy.get(".net-element")
        .its("length")
        .should("eq", componentCounts + 1);
    });
  });

  it("Can select a component", () => {
    //   deselect component
    cy.get(".network-field").click(350, 300);
    cy.get(".net-element--active").should("not.exist");

    cy.get(".net-element")
      .last()
      .click();
    cy.get(".net-element--active")
      .its("length")
      .should("eq", 1);
  });

  it("Can delete a component", () => {
    cy.get(".net-element")
      .its("length")
      .as("componentsCount");
    cy.get(".net-element--active").type("{del}");
    cy.get("@componentsCount").then((componentCounts) => {
      cy.get(".net-element")
        .its("length")
        .should("eq", componentCounts - 1);
    });
  });

  it("Can create a connection", () => {
    cy.get(".svg-arrow_line")
      .its("length")
      .as("connectionCount");

    //   create 2 components
    createRandomElement(50, 300);
    createRandomElement(250, 300);
    cy.get(".net-element")
      .eq(5)
      .find(".output-dot")
      .first()
      .trigger("mousedown");
    cy.get(".net-element")
      .eq(6)
      .find(".input-dot")
      .first()
      .trigger("mouseup");

    cy.get("@connectionCount").then((connectionCount) => {
      cy.get(".svg-arrow_line")
        .its("length")
        .should("eq", connectionCount + 1);
    });
  });

  it("Can delete a connection", () => {
    cy.get(".svg-arrow_line")
      .its("length")
      .as("connectionCount");

    //   create 2 components
    cy.get(".svg-arrow_line")
      .last()
      .click();
    cy.get(".svg-arrow_line.is-focused").type("{del}");

    cy.get("@connectionCount").then((connectionCount) => {
      cy.get(".svg-arrow_line")
        .its("length")
        .should("eq", connectionCount - 1);
    });
  });

  it("Can update the settings in a component (just neurons in a Dense)", () => {
    createElement("Deep Learning", "Dense", { X: 550, Y: 300 });
    cy.get(".toggle-button").click();
    cy.get(".components-settings-lock-wrapper")
      .find("#tutorial_neurons > input")
      .clear()
      .type("5{enter}");

    cy.get(".network-field").click();
    cy.get(".net-element")
      .last()
      .click();
    cy.get(".components-settings-lock-wrapper")
      .find("#tutorial_neurons > input")
      .should("have.value", "5");
  });

  it("Can zoom in/out", () => {
    cy.get(".net-element")
      .first()
      .then(($target) => {
        cy.log($target[0]);
        const elementWidth = $target[0].getBoundingClientRect().width;
        cy.get(".network-field").click(0, 0);
        cy.get(".workspace-scale_input input")
          .clear()
          .type("50 {enter}");
        cy.get(".net-element")
          .first()
          .then(($x) =>
            cy
              .wrap($x[0].getBoundingClientRect())
              .its("width")
              .should("eq", elementWidth / 2)
          );

        cy.get(".workspace-scale_input input")
          .clear()
          .type("200 {enter}");
        cy.get(".net-element")
          .first()
          .then(($x) =>
            cy
              .wrap($x[0].getBoundingClientRect())
              .its("width")
              .should("eq", elementWidth * 2)
          );
      });
    cy.get(".workspace-scale_input input")
      .clear()
      .type("100 {enter}");
  });
});

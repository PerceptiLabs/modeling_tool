describe("logout", () => {
  beforeEach(() => {
    cy.fixture("userCredentials").then((user) => {
      cy.kcLogin(user.email, user.password);
    });
  });

  it("should logout with correct credentials", () => {
    cy.visit("/");

    cy.get(".profile-item-drop-down").invoke("show");

    cy.get(".profile-item-drop-down .sign-out-all").click();

    cy.location("origin", { timeout: 20 * 1000 }).should(
      "eq",
      `${Cypress.env("KEYCLOAK_BASE_URL")}`
    );
  });
});

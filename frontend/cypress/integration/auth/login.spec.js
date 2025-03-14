describe('authentication', () => {

  beforeEach(() => cy.kcLogout());

  it('should login with correct credentials', () => {
    cy.visit('/');

    cy.location('origin', { timeout: 20 * 1000 }).should('eq', Cypress.env('KEYCLOAK_BASE_URL'));

    cy.fixture('userCredentials').then((user) => {
      cy.get('#username').type(user.email);
      cy.get('#password').type(user.password);

      cy.get('#kc-login').click();

      cy.location('href', { timeout: 20 * 1000 }).should('eq', `${Cypress.env('APP_URL')}`)
    })
  });

  it('should fail with incorrect credentials', () => {
    cy.visit('/');

    cy.location('origin', { timeout: 20 * 1000 }).should('eq', Cypress.env('KEYCLOAK_BASE_URL'));

    cy.fixture('userCredentials').then((user) => {
      cy.get('#username').type(user.email);
      cy.get('#password').type('random password');

      cy.get('#kc-login').click();

      cy.get('.alert.alert-error').should('be.visible');
    })
  });
})
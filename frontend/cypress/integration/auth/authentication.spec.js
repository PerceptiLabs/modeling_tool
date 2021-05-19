describe('authentication', () => {
  
  beforeEach(() => cy.kcLogout());

  it('should login with correct credentials', () => {
    cy.visit('/');

    cy.location('host', { timeout: 20 * 1000 }).should('eq', 'keycloak.dev.perceptilabs.com:8443');

    cy.fixture('userCredentials').then((user) => {
      cy.get('#username').type(user.email);
      cy.get('#password').type(user.password);

      cy.get('#kc-login').click();

      cy.location({ timeout: 20 * 1000 }).should((location) => {
        expect(location.host).to.eq('localhost:8080')
        expect(location.pathname).to.eq('/')
      })
    })
  });

  it('should fail with incorrect credentials', () => {
    cy.visit('/');

    cy.location('host', { timeout: 20 * 1000 }).should('eq', 'keycloak.dev.perceptilabs.com:8443');

    cy.fixture('userCredentials').then((user) => {
      cy.get('#username').type(user.email);
      cy.get('#password').type('random password');

      cy.get('#kc-login').click();

      cy.get('.alert.alert-error').should('be.visible');
    })
  });
})
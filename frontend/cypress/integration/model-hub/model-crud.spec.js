describe('model-hub', () => {
    beforeEach(() => {
        cy.fixture('userCredentials').then((user) => {
            cy.kcLogin(user.email, user.password);
        })
    });

    it('should open model hub without login form', () => {
        cy.visit('/');
        cy.wait(5 * 1000);

        cy.location('host', { timeout: 20 * 1000 }).should('eq', 'localhost:8080');

        cy.get('.page-title').should('be.visible');
    });
})
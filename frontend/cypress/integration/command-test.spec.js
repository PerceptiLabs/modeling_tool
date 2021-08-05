describe('commands', () => {
    beforeEach(() => {
        cy.fixture('userCredentials').then((user) => {
            cy.kcLogin(user.email, user.password);
        })
    });

    it('delete all models', () => {
        cy.deleteAllModels();
        
        cy.visit('/');
        
        cy.get('.models-list').should('be.visible');
        cy.get('.models-list-row.model-list-item').should('not.exist');
    });

    it('create mnist model', () => {
        cy.createMnistModel('Model 1');
        cy.createMnistModel('Model 2');
        cy.createMnistModel('Model 3');

        cy.visit('/');

        cy.get('.models-list').should('be.visible');
        cy.get('.models-list-row.model-list-item').should('have.length', 3);
    });
})
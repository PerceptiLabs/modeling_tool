describe('model-hub', () => {
    beforeEach(() => {
        cy.fixture('userCredentials').then((user) => {
            cy.kcLogin(user.email, user.password);
        })
    });
})
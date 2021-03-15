it('Should skip first time log in modal', () => {
  cy.get('.next-step').click();
  cy.get('.next-step').click();
  cy.get('.get-started').click();
});
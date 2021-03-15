it('Should open report modal', () => {
  cy.get('[data-testing-target="report-modal-btn"]').click();
  cy.get('[data-testing-target="report-modal"]').should('be.visible');
  cy.get('button').contains('Cancel').click();
});
it('Should remove models', () => {
  cy.get('.wrapper > :nth-child(1)').click();
  cy.get('.model-list-header > .column-1 > .btn-round-icon').click();
  cy.get('.right-side > :nth-child(3)').click();
  cy.get('.popup_foot').contains('Delete').click();
});
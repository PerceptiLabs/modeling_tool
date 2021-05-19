it('Should create and remove the output', () => {
  cy.get('.output-container:eq(0)').rightclick();
  cy.get('.output-context-button').click();
  cy.get('.output-container')
      .should(($inputsEl) => {
        expect($inputsEl).to.have.length(3);
      })
  cy.get('.output-container:eq(1)').rightclick();
  cy.get('.output-context-button:eq(1)').click();
  cy.get('.output-container')
      .should(($inputsEl) => {
        expect($inputsEl).to.have.length(2);
      })
});
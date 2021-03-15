it('Should create and remove the input', () => {
  cy.get('.input-container').rightclick();
  cy.get('.input-context').click();
  cy.get('.input-container')
      .should(($inputsEl) => {
        expect($inputsEl).to.have.length(2);
      })
  cy.get('.input-container:eq(1)').rightclick();
  cy.get('.input-context-button:eq(1)').click();
  cy.get('.input-container')
      .should(($inputsEl) => {
        expect($inputsEl).to.have.length(1);
      })
});
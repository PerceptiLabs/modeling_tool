it('Should open and close mini-map', () => {
  cy.get('[data-testing-target="mini-map-checkbox"]').click();
  cy.get('[data-testing-target="mini-map"]').should('be.visible');
  cy.get('[data-testing-target="mini-map-checkbox"]').click();

  cy.get('[data-testing-target="mini-map"]')
    .should($el => {
      expect($el).to.have.length(0);
    })

});
it('Should zoom in and out ', () => {
  cy.get('.net-element:eq(0)')
    .then($target => {
      cy.log($target[0]);
      const elementWidth =  $target[0].getBoundingClientRect().width;
      cy.get('.network-field').click(0, 0);
      cy.get('.workspace-scale_input input').clear().type('50 {enter}');
      cy.get('.net-element:eq(0)')
      .then($x => cy.wrap($x[0].getBoundingClientRect()).its('width').should('eq', elementWidth / 2));
      
      cy.get('.workspace-scale_input input').clear().type('200 {enter}');
      cy.get('.net-element:eq(0)')
      .then($x => cy.wrap($x[0].getBoundingClientRect()).its('width').should('eq', elementWidth * 2));
    });
    cy.get('.workspace-scale_input input').clear().type('100 {enter}');

});
it('Should remove a component', () => {
  cy.get('.net-element_btn').first().click();
  cy.get('.workspace-scale_input input').clear().type('{backspace}');
  cy.get('.workspace-scale_input input').clear().type('100 {enter}');
  cy.get('.net-element')
    .should(($netEle) => {
      expect($netEle).to.have.length(1);
    })
  });
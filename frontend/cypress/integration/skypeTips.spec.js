
  it('Should skype the tips', () => {
    cy.get('.tutorial-notification-hidetips > span').click();
    cy.get('.checklist-skip > span').click();
  });